# SwiftUI Vision and Core ML live-observation review route

This route turns a live camera frame into a reviewable observation while keeping capture, analysis, model output, UI state, proposals, and side effects separate. It is a route sketch for a named iOS target, not proof that any particular model, camera, device, or release configuration works.

Pairs with [SwiftUI Vision and Core ML live-observation review](../42-framework-deep-dives/95-swiftui-vision-core-ml-live-observation-review.md), [SwiftUI media capture and review](119-swiftui-media-capture-and-review-route.md), and [Core ML model inference](90-core-ml-model-inference-capability-route.md).

## Route map

~~~text
target and NSCameraUsageDescription
  -> camera authorization
  -> AVCaptureSession configuration
  -> AVCaptureVideoDataOutput delegate queue
  -> frame admission and latest-frame policy
  -> CVPixelBuffer, timestamp, orientation, and source revision
  -> VNImageRequestHandler
  -> Vision request or VNCoreMLRequest
  -> typed observation normalization
  -> coordinate mapping and freshness
  -> MainActor SwiftUI projection
  -> optional on-device AI proposal
  -> validation
  -> explicit user commit
~~~

Use the narrowest route that satisfies the product outcome. If the feature only needs a still image, use a still-image or photo route rather than creating an always-on analyzer.

## Capability and target gates

| Gate | Check | Failure state |
| --- | --- | --- |
| Camera privacy | NSCameraUsageDescription in the signed target | Explain why access is needed. |
| Runtime authorization | AVCaptureDevice status and request result | Denied, restricted, or ask state. |
| Capture input | Intended device and format can be added | Camera unavailable or unsupported. |
| Analysis output | Video-data output can be added and configured | Preview-only or unavailable. |
| Model asset | Compiled model exists and loads | On-device analysis unavailable. |
| Compute policy | MLModelConfiguration is supported | Use a supported fallback or disable. |
| Vision revision | Selected request revision is supported | Reconfigure or show incompatibility. |
| UI route | MainActor presentation is still active | Drop result as stale. |
| Commit authority | Deterministic validator and user intent exist | Keep proposal-only state. |

Do not use a successful camera permission request as proof that a video-data output, model, or physical feature is ready.

## Route states

Represent combined state explicitly:

~~~swift
enum LiveObservationState {
    case unavailable(reason: String)
    case requestingCameraAccess
    case configuring
    case modelLoading
    case ready
    case sampling(lastFrameID: UInt64?)
    case reported(ObservationSnapshot)
    case stale(ObservationSnapshot)
    case proposal(ProposalSnapshot)
    case failed(message: String)
}
~~~

Keep this product state separate from AVCaptureSession running state, VNRequest completion, MLModel readiness, and any domain state. A session can be running while the analyzer is unavailable, and a model can be loaded while the camera is denied.

## Frame admission

Use one serial processing owner for the simple route:

1. Receive a CMSampleBuffer on the delegate queue.
2. Read the CVPixelBuffer and presentation timestamp.
3. Increment a frame sequence.
4. If a request is already in flight, drop or replace according to the documented policy.
5. Capture orientation, dimensions, region of interest, and session revision.
6. Run the requests on the same bounded owner.
7. Publish only if the session revision is still current.

The preview may continue while analysis is paused. The UI should say that analysis is sampling selected frames rather than implying every preview frame was analyzed.

## Vision request pipeline

For each admitted frame:

1. Construct VNImageRequestHandler with the pixel buffer or sample buffer and orientation.
2. Configure the request’s crop-and-scale policy.
3. Apply a known request revision when reproducibility matters.
4. Perform the request on the analysis queue.
5. Normalize the request’s result type into a product observation.
6. Preserve source frame identifier, timestamp, request type, and revision.
7. Convert normalized geometry with one coordinate adapter.
8. Publish a value snapshot to the MainActor.

For object recognition, preserve observation confidence and classification label confidence. For text, preserve the candidate list or selected candidate and source region. For pose, preserve joint names and point confidence. For a general Core ML predictor, inspect feature values against the model description.

## Model loading and ownership

Load the compiled model asynchronously before the live route begins when practical:

~~~text
model URL
  -> MLModelConfiguration
  -> MLModel.load
  -> VNCoreMLModel
  -> VNCoreMLRequest
  -> serialized request execution
~~~

Choose compute units intentionally. all lets the OS select available units, while CPU-only can be useful when the app may run in the background or compete for GPU resources. Check available compute devices when a target-specific policy matters.

Keep one MLModel instance on one thread or dispatch queue at a time. The request owner, model owner, and frame-admission policy must agree on serialization. Do not create a new model per frame or invoke one instance from unbounded concurrent tasks.

## Coordinate route

Use a single value type:

~~~swift
struct OverlayGeometry {
    let normalizedVisionRect: CGRect
    let imageRect: CGRect
    let viewRect: CGRect
    let sourceFrameID: UInt64
    let isMirrored: Bool
}
~~~

The adapter must account for the lower-left origin used by classic Vision detected-object coordinates, image orientation, camera mirroring, aspect fit or fill, crop, safe area, and the current container size. Store the source frame ID with the geometry so a tap cannot apply to a later frame.

## Provenance and freshness

Every result should carry:

~~~swift
struct ObservationSource {
    let frameID: UInt64
    let presentationTime: CMTime
    let requestName: String
    let requestRevision: Int?
    let modelID: String?
    let modelVersion: String?
    let inputSize: CGSize
    let orientation: CGImagePropertyOrientation
    let regionOfInterest: CGRect?
}
~~~

Use this source to derive reported, low-confidence, stale, and unavailable states. If the screen changes source, camera, orientation, model, or request revision, increment a session revision and reject late completions.

## Local AI proposal route

Only pass compact, redacted, typed context to the on-device language model:

~~~text
selected observation source
  -> redaction and deterministic formatting
  -> local explanation or structured proposal
  -> attach source revision and warnings
  -> user reviews and edits
  -> deterministic validation
  -> explicit commit or reject
~~~

The proposal cannot invent an observation, select a person by fuzzy label, bypass a camera permission, convert confidence into certainty, or execute an external action. If the source is stale or the model is unavailable, the route should remain usable without AI.

## SwiftUI presentation route

Use native controls for user intent:

- Button for pause, retake, capture, review, reject, and apply;
- Toggle only for a real app setting, not as a proxy for a physical or model state;
- Sheet or inspector for source and proposal review;
- accessibility labels and values for every observation;
- a GlassEffectContainer or equivalent functional glass group only for related controls;
- standard material or opaque fallback for content and reduced-transparency settings.

The UI should never imply that a label is verified identity or that an AI proposal is committed state.

## Cancellation and recovery

Cancel or invalidate at these boundaries:

- feature leaves the active scene;
- camera permission changes;
- capture session stops or is interrupted;
- model loading is cancelled;
- a new session revision replaces the old one;
- user switches camera or source frame;
- proposal source becomes stale;
- app enters a state where side effects are no longer authorized.

Recovery should preserve a reviewable selected frame when appropriate, but never keep a stale live overlay marked as current.

## Evidence route

For a named feature, collect evidence in order:

1. target privacy and capability configuration;
2. permission grant, denial, and revocation;
3. physical camera preview and orientation;
4. admitted-frame count, drop policy, and latency;
5. Vision request revision and coordinate mapping;
6. model asset, output contract, and compute policy;
7. typed observation fixtures;
8. proposal review and rejection;
9. accessibility and reduced-effects task completion;
10. physical performance, archive, TestFlight, and release checks.

A compile, preview, model load, or simulator frame is one narrow step in this route and cannot replace the later evidence.

## Sources

- [AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [Requesting authorization to capture and save media](https://developer.apple.com/documentation/avfoundation/requesting-authorization-to-capture-and-save-media)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNRequest](https://developer.apple.com/documentation/vision/vnrequest)
- [VNObservation](https://developer.apple.com/documentation/vision/vnobservation)
- [VNRecognizedObjectObservation](https://developer.apple.com/documentation/vision/vnrecognizedobjectobservation)
- [VNRecognizedTextObservation](https://developer.apple.com/documentation/vision/vnrecognizedtextobservation)
- [VNRecognizedPointsObservation](https://developer.apple.com/documentation/vision/vnrecognizedpointsobservation)
- [VNCoreMLModel](https://developer.apple.com/documentation/vision/vncoremlmodel)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Recognizing objects in live capture](https://developer.apple.com/documentation/vision/recognizing-objects-in-live-capture)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
