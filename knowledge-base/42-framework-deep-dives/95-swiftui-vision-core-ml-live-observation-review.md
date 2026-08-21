# SwiftUI Vision and Core ML live-observation review

This deep dive covers the SwiftUI boundary around a live camera and on-device image analysis: camera permission, capture-session ownership, frame admission, Vision request revisions, normalized geometry, typed observations, Core ML model loading and compute policy, cancellation, source provenance, reviewable local-AI proposals, Liquid Glass shells, accessibility, privacy, energy, and physical-device proof.

It extends [SwiftUI media capture and review](88-swiftui-media-capture-and-review.md), [VisionKit and reviewable capture](../41-framework-deep-dives/05-visionkit-and-reviewable-capture.md), [Core ML model lifecycle and inference](../42-framework-deep-dives/66-core-ml-model-lifecycle-and-inference.md), and [Vision and Core ML pipelines](../30-on-device-ai/04-vision-ocr-and-camera.md).

## The live-analysis contract

~~~text
target and camera authorization
  -> AVCaptureSession input and video-data output
  -> serial sample-buffer queue
  -> bounded frame-admission policy
  -> CVPixelBuffer plus orientation and timestamp
  -> Vision request handler and selected revision
  -> typed observation or Core ML output
  -> normalized geometry, confidence, and provenance
  -> MainActor SwiftUI projection
  -> optional local-AI proposal
  -> deterministic validation and explicit user commit
  -> physical-device and release evidence
~~~

The camera frame, Vision observation, Core ML prediction, language-model explanation, user decision, and side effect are different facts. A SwiftUI overlay can display a prediction without making it true, current, safe, or suitable for a medical, legal, identity, or security claim.

| Fact | Owner | UI meaning |
| --- | --- | --- |
| Camera permission | System and AVCaptureDevice | The app may or may not request frames. |
| Capture session | AVFoundation coordinator | A route that may deliver frames. |
| Sample buffer | AVFoundation callback | One source frame with format and timing. |
| Vision request | Vision framework | An algorithm invocation with a class and revision. |
| Observation | Vision | A result tied to the processed image and request. |
| Core ML prediction | Core ML model | Output whose confidence semantics come from the model. |
| Rendered overlay | SwiftUI coordinate adapter | A presentation after geometry conversion. |
| AI proposal | On-device model adapter | Untrusted wording or suggested next step. |
| User decision | Product flow | Explicit acceptance, rejection, edit, or dismissal. |
| Domain result | Deterministic app/system boundary | The only place that establishes a committed outcome. |

Do not use a colored box, confidence percentage, model label, or glass animation as a substitute for source, freshness, or result evidence.

## Camera permission and capture ownership

Before setting up a camera route:

1. Confirm the target contains NSCameraUsageDescription with a concrete purpose.
2. Check AVCaptureDevice authorizationStatus for video.
3. Request access when the person starts the camera feature if capture is not the app’s primary purpose.
4. Treat denied and restricted access as normal recovery states.
5. Configure session inputs and outputs on an owned queue.
6. Stop the session and detach work when the feature leaves its active lifecycle.

Apple’s capture-authorization guidance says the privacy key must exist before the app requests access or attempts to use the camera. A source import, preview placeholder, or simulator feed does not prove that the signed target has the required privacy configuration.

AVCaptureSession coordinates capture inputs and outputs. For live Vision/Core ML analysis, AVCaptureVideoDataOutput is the processing output. Keep these paths separate:

| Path | Responsibility |
| --- | --- |
| Preview | Current camera content with correct aspect, orientation, and privacy state. |
| Analysis | Bounded frame admission and Vision/Core ML work. |
| Review | Typed observations, freshness, confidence, and source details. |
| Commit | Deterministic user-approved action, if the feature has one. |

Do not make a camera preview imply that analysis is active. Do not make a live badge imply that the latest result is current if the analyzer is throttling or dropping frames.

## Frame queue and backpressure

Set the sample-buffer delegate on a deliberate queue. Apple documents that callbacks arrive on the queue supplied to setSampleBufferDelegate. Use a small serial processing queue for a simple analyzer, or an explicitly bounded design for multiple stages.

AVCaptureVideoDataOutput exposes alwaysDiscardsLateVideoFrames. When analysis cannot keep up, latest-frame admission is often more truthful for a live overlay than displaying a result from a frame already far behind the preview.

| Policy | Fit | Risk |
| --- | --- | --- |
| Latest frame wins | Live overlay or guidance | Temporal tracking must tolerate gaps. |
| Every frame | Offline or deterministic batch analysis | Queue, memory, latency, and thermal growth. |
| Fixed sampling interval | Stable cadence and energy control | Short-lived events can be missed. |
| Pause while reviewing | User-selected still frame | Analysis is not continuous during review. |

Use minFrameDuration or an equivalent capture-rate policy when cadence matters. Choose a native or efficient pixel format. Apple warns that forcing non-native formats such as default BGRA can increase conversion and memory cost; measure the selected format on target hardware.

The callback should capture the presentation timestamp and frame identifier, apply the admission policy, run or enqueue bounded requests, publish a small immutable result, release the buffer, and return promptly. Do not update SwiftUI directly from the capture queue, retain a queue of full-resolution buffers, or create an unbounded Task for every callback.

## Orientation, crop, region of interest, and geometry

Vision needs the orientation of the image it analyzes. Pass the orientation consistently to the request handler and use the same source geometry for the preview transform. A camera preview can be rotated, mirrored, aspect-filled, cropped, or letterboxed independently of the pixel buffer. A bounding box that looks right in a square test image can be wrong on a portrait camera feed.

Classic Vision detected-object coordinates are normalized to the processed image dimensions with the origin at the image’s lower-left corner. A SwiftUI layout generally uses a top-left visual origin. The transformation has at least these stages:

~~~text
Vision normalized lower-left rectangle
  -> lower-left to top-left image rectangle
  -> orientation and mirroring transform
  -> aspect-fit or aspect-fill content transform
  -> preview/container coordinate rectangle
~~~

VNImageRectForNormalizedRect can help convert normalized Vision rectangles to image-space pixels, but it does not know the final SwiftUI container’s crop, safe area, or camera mirroring policy. If the preview uses aspect fill, compute the visible source rect and apply the same scale and offset to overlays. Keep a single tested coordinate adapter instead of scattering flips through views.

If using a region of interest, record it in result provenance. A model confidence value for a cropped region is not confidence for the entire camera frame. When a person taps an observation, map the UI point back through the inverse transform and verify that the target still belongs to the same frame revision.
## Backpressure, cancellation, and stale-result protection

The minimum safe design has one admission gate and one result gate:

~~~text
capture callback
  -> if analysis is busy, drop or replace according to policy
  -> admit frame N with source revision R
  -> perform bounded requests
  -> before publishing, require R to still be current
  -> publish only if the feature is active and frame N is not superseded
~~~

Use a frame sequence or session revision. A result arriving after a route change must be ignored even if its request succeeded. If an AI proposal was generated from frame N, it must carry frame N’s observation revision and become stale when the person reviews frame N+1 or changes the source selection.

Cancellation is explicit at each boundary:

- stop AVCaptureSession when the product no longer needs frames;
- cancel a Task that owns asynchronous model loading;
- cancel or invalidate in-flight analysis where the selected API supports it;
- stop publishing to a closed view or session;
- close any continuation exactly once;
- release buffers and model intermediates promptly.

Do not claim that a dropped frame was analyzed. Say that live analysis is sampling or show the last analyzed time. If analysis falls behind, prefer a stale or throttled state over animating a result as current.

## Typed observation and source provenance

Normalize framework results into a product type that cannot lose source context:

~~~swift
struct ObservationEnvelope<Value: Sendable>: Sendable {
    let frameID: UInt64
    let presentationTime: CMTime
    let inputSize: CGSize
    let orientation: CGImagePropertyOrientation
    let requestName: String
    let requestRevision: Int?
    let modelIdentifier: String?
    let modelVersion: String?
    let confidence: Float?
    let normalizedRegion: CGRect?
    let value: Value
}
~~~

The exact type may differ by target and Swift concurrency mode. The invariant is more important than the spelling: every displayed observation should be traceable to an input frame, request or model version, geometry policy, and freshness state.

| Lifecycle | Example copy |
| --- | --- |
| unavailable | Camera or model unavailable. |
| loading | Preparing on-device analysis. |
| analyzing | Analyzing the latest admitted frame. |
| reported | Observed in frame captured at 10:42:08. |
| low confidence | Possible match; review before using. |
| stale | Last result from 2.4 seconds ago. |
| failed | Analysis stopped; camera input was not usable. |

Keep raw frames out of logs by default. If a debug build records a frame or observation fixture, label it as test data, redact identifiers, and define retention.

## Local AI proposal boundary

Use on-device language intelligence as an optional explanation or proposal layer over typed, selected observations:

~~~text
selected observation envelope
  -> deterministic redaction and compact structured context
  -> on-device language-model session
  -> proposal with source frame and model revision
  -> human-readable uncertainty and warnings
  -> person reviews or edits
  -> deterministic validator
  -> explicit product action
~~~

The language model must not select a person or object from an untrusted label, invent a camera observation, infer medical or legal truth, or directly trigger a physical or account side effect. Local availability is a privacy and latency advantage, not evidence that the proposal is correct.

For any action, show the exact source observations and proposed parameters. If the source is stale, low-confidence, missing, or from an unsupported model revision, require refresh or reject the proposal. Keep proposal, validation, and commit as separate types and test rejection.

## SwiftUI and Liquid Glass review surface

Use a layered screen:

~~~text
camera content layer
  -> sparse observation overlay
  -> functional control layer
  -> review/detail surface
  -> optional action confirmation
~~~

Apple’s Liquid Glass guidance places the material in a distinct functional layer for controls and navigation. Keep the camera feed and observation content readable; do not cover every detection box, preview region, or result card with custom glass. Use standard materials or opaque surfaces for content when they provide clearer contrast.

Glass groups can contain related controls such as pause, capture, review, or settings. A glass button must not mean that the model is correct. Use text, labels, and state icons to communicate analyzing, stale, low confidence, and unavailable. Respect increased contrast and reduced transparency, and provide an equivalent opaque or standard-material hierarchy.

For observation overlays:

- group a box with its label, confidence semantics, and source state;
- provide an accessibility element that describes the observation without requiring a person to find the box visually;
- expose the original text candidate or identifier when useful, without presenting a technical label as a polished claim;
- make pause, retake, review, and dismiss reachable by VoiceOver, Voice Control, Switch Control, keyboard, and pointer;
- keep tap targets usable after Dynamic Type and localization expand labels;
- ensure Reduce Motion does not hide the transition from stale to reported.

## Privacy, energy, and performance

Camera frames can contain faces, screens, documents, addresses, and other sensitive content. The default route should be on-device and ephemeral unless the product has an explicit upload need and consent. Define whether frames are retained, whether observations leave the device, whether logs include text or coordinates, whether the person can pause or delete captured content, and how screenshots, recordings, and support exports are handled.

Measure on representative physical devices:

- frame admission rate and dropped-frame count;
- analyzer latency from presentation timestamp to publication;
- preview-to-overlay staleness;
- CPU, GPU, Neural Engine choice, and memory;
- energy and thermal behavior over a sustained session;
- background, lock, interruption, and camera-revocation behavior;
- large-text, VoiceOver, increased-contrast, and reduced-motion task completion.

A fast simulator preview is not a physical camera or thermal result. A model benchmark number is not end-to-end user latency.

## Physical-device and release boundary

Before calling the route ready, prove the intended claim with the intended target:

1. The signed archive contains NSCameraUsageDescription and the selected target configuration.
2. A physical device grants, denies, and later revokes camera access.
3. Real orientation, mirroring, crop, and overlay mapping are correct.
4. The analyzer drops or throttles frames according to the documented policy.
5. Results remain tied to frame identity, timestamps, request revisions, and model version.
6. A physical device runs the model under representative duration and thermal conditions.
7. Accessibility settings allow the complete review task.
8. AI proposals can be rejected, edited, or made stale before any commit.
9. Archive, TestFlight, and release metadata match privacy and capability claims.

A preview, bounding box, confidence number, simulator frame, model load, or compile proves only the corresponding narrow fact.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [AVCaptureVideoDataOutput sample-buffer delegate](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutputsamplebufferdelegate)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [ImageRequestHandler](https://developer.apple.com/documentation/vision/imagerequesthandler)
- [VNRequest](https://developer.apple.com/documentation/vision/vnrequest)
- [VNObservation](https://developer.apple.com/documentation/vision/vnobservation)
- [VNDetectedObjectObservation](https://developer.apple.com/documentation/vision/vndetectedobjectobservation)
- [VNRecognizedObjectObservation](https://developer.apple.com/documentation/vision/vnrecognizedobjectobservation)
- [VNRecognizedTextObservation](https://developer.apple.com/documentation/vision/vnrecognizedtextobservation)
- [VNRecognizedPointsObservation](https://developer.apple.com/documentation/vision/vnrecognizedpointsobservation)
- [VNHumanBodyPoseObservation](https://developer.apple.com/documentation/vision/vnhumanbodyposeobservation)
- [VNCoreMLModel](https://developer.apple.com/documentation/vision/vncoremlmodel)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Recognizing objects in live capture](https://developer.apple.com/documentation/vision/recognizing-objects-in-live-capture)
- [Recognizing text in images](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [Detecting human body poses in images](https://developer.apple.com/documentation/vision/detecting-human-body-poses-in-images)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Materials](https://developer.apple.com/design/human-interface-guidelines/materials)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
## Vision request lifecycle and revisions

VNImageRequestHandler processes one image and performs one or more image-analysis requests. For a live route, create the handler with the current pixel buffer or sample buffer and the intended orientation, then perform the requests on the analysis owner’s queue.

Vision request classes can expose currentRevision, defaultRevision, and supportedRevisions. A revision identifies the algorithm implementation used for a request. Treat it as stored provenance:

| Provenance field | Why it matters |
| --- | --- |
| Request type | Distinguishes text, object, rectangle, barcode, pose, tracking, and custom model work. |
| Revision | Prevents comparison to an incompatible algorithm version. |
| Model identifier/version | Establishes which Core ML asset produced a prediction. |
| Input orientation | Explains geometry and orientation-sensitive behavior. |
| Source frame identifier | Prevents a stale completion replacing a newer frame. |
| Presentation timestamp | Supports freshness and temporal ordering. |

Set a revision deliberately when repeatable behavior matters and verify that the selected revision is supported on the deployment target. If the default revision changes with a linked SDK, a confidence or geometry comparison across builds is not automatically apples-to-apples.

Completion handlers may run on the request owner’s queue. Convert results into value snapshots, then publish to the MainActor. If a view disappears, cancel the analyzer’s work or invalidate its session revision so an old completion cannot resurrect a stale overlay.

## Observation types and confidence semantics

| Observation family | Useful projection | Boundary |
| --- | --- | --- |
| VNRecognizedObjectObservation | Bounding box plus ordered classification labels | A label is a model classification, not verified identity. |
| VNRecognizedTextObservation | Location plus top text candidates | A candidate string needs review, language, and source-frame context. |
| VNRecognizedPointsObservation and pose subclasses | Named points and point confidence | Points can be absent or low-confidence. |
| VNDetectedObjectObservation | Detected or tracked bounding box | Tracking continuity is not identity or object persistence. |
| VNClassificationObservation | Identifier and confidence | Technical labels are not automatically end-user copy. |
| VNPixelBufferObservation | Image-to-image output | Another image result is not semantic truth. |
| VNCoreMLFeatureValueObservation | General feature-value output | Interpret only against the model feature description. |

VNRecognizedObjectObservation labels are ordered by classification confidence, but the observation confidence and label confidence are separate values. Preserve both rather than displaying one number as universal certainty. Apple documents that Vision normally normalizes confidence to 0.0 through 1.0, while values from a VNCoreMLRequest can be forwarded from the Core ML model as-is and may not be normalized. Record the source and semantics before formatting a percentage.

VNRecognizedTextObservation contains recognized text and location; ask for top candidates and expose uncertainty when a person must verify a string. A text result should not silently become a destructive command, contact, address, medical interpretation, or legal record.

Pose observations expose named points or point groups with their own confidence. Apple’s pose guidance calls out framing and scene conditions that affect accuracy, including subject size, occlusion, clothing, and dense crowds. A pose skeleton is an observation of image features, not a diagnosis or a guarantee of safe form.

For newer Swift Vision APIs exposed by the selected SDK, observation values may include a UUID, confidence, time range, and originating request descriptor. Keep the same conceptual provenance when using the modern surface, and check availability because Apple marks some newer types as beta or subject to change.

## Core ML model loading and compute policy

Core ML models encapsulate prediction behavior, input/output descriptions, and configuration. Prefer an Xcode-generated model wrapper when it matches the target asset and gives the project a typed contract. When loading a compiled asset directly, use MLModel.load asynchronously with an MLModelConfiguration.

| Setting | Product question |
| --- | --- |
| MLComputeUnits.all | May the OS choose available units, including the Neural Engine when available? |
| MLComputeUnits.cpuOnly | Is CPU-only behavior needed because the app may be backgrounded or compete for GPU? |
| CPU and GPU / CPU and Neural Engine | Does a known target policy justify excluding one class of unit? |
| availableComputeDevices | Which devices can the model use at runtime? |
| modelDescription | What input/output feature contract must the adapter satisfy? |

Apple’s Core ML documentation says to use an MLModel instance on one thread or one dispatch queue at a time. Serialize calls on the model owner or create separate model instances for separate queues. Do not share one model instance across arbitrary frame tasks.

Model readiness is not model validity. Verify that the compiled asset and expected version are loaded, pixel format and dimensions match, crop and orientation match, output names and types match, target compute support exists, and memory and thermal behavior are acceptable. A model error must become a bounded unavailable state.

For a live analyzer, load the model before expensive capture work when practical, or present a loading state and drop frames while it is unavailable. Do not block the main actor or create duplicate model instances every time a view appears.

## Vision plus Core ML result contract

A VNCoreMLRequest can produce different observation families depending on the model description: classification observations for a classifier, pixel-buffer observations for image-to-image output, or feature-value observations for general predictors. The adapter must inspect the model contract rather than assume every model returns labels.

Set the crop-and-scale policy deliberately. The model may be correct for a center crop while the preview shows aspect fill or a different region. Record the crop policy with the result and test objects near every edge. If the model requires an input feature outside Vision, use the documented feature-provider boundary rather than mutating a view or global singleton.

A model label is not a user-facing claim. Map technical identifiers through a versioned presentation table, preserve an unknown-label path, and keep the original identifier available in diagnostics.
