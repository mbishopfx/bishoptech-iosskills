# Vision and Core ML Pipelines

## Capability

Vision and Core ML are the right routes when the output is an image observation, classifier result, detector, embedding, or model prediction. Foundation Models can interpret text and multimodal prompts, but it should not replace a narrower, measurable computer-vision pipeline when that pipeline is the actual product requirement.

## Choose the route

| Need | Route | Output boundary |
| --- | --- | --- |
| Text in an image | Vision text recognition | Observations with confidence/geometry; validate and review. |
| Faces, body/hand pose, objects, image quality | Vision request family | Structured observations, not identity or intent by default. |
| Custom classifier/detector/regressor | Core ML model and generated wrapper | Model-defined input/output with device performance constraints. |
| Camera live stream | AVFoundation/Vision or VisionKit | Permission, frame rate, backpressure, and physical-device behavior. |
| Rich language explanation of a bounded observation | Feed validated observations into Foundation Models | Keep raw pixels and sensitive data minimized. |

## Pipeline boundary

`image/frame -> preprocessing -> Vision/Core ML request -> observation/prediction -> validation -> reviewable domain draft`

Keep preprocessing and model versions explicit. Store confidence and provenance when they affect review. Do not save the observation directly as a “fact” unless the product’s validation policy supports that claim.

## Core ML route

1. Confirm the model’s input shapes, output types, metadata, and deployment targets.
2. Prefer the Xcode-generated model wrapper for a bundled model when it expresses the interface clearly.
3. Use `MLModel` directly when the app downloads/compiles a model or needs lower-level control.
4. Configure compute units and memory behavior for the supported device range.
5. Serialize access to a model instance or create separate instances for concurrent work according to the API’s requirements.
6. Measure prediction latency, memory, thermal impact, and accuracy on representative devices.

## Vision route

Create a request for the actual observation, configure revision/options for the selected SDK, submit it on an appropriate queue, then map observations into app-owned types. Camera UI, photo import, Vision requests, and review forms should remain separate layers so a person can correct an extraction without rerunning the entire capture flow.

## Privacy and fallback

- Keep raw images on device unless upload is necessary and disclosed.
- Crop or redact before processing when the feature does not need the whole image.
- If the model is unavailable, return manual entry or “save for later processing” rather than inventing a result.
- Do not infer identity, health status, emotion, or sensitive traits from a generic observation without a separately justified and reviewed product design.

## Verification route

- Build a labeled test set covering lighting, orientation, blur, occlusion, language, skin tones, backgrounds, and negative examples.
- Score false positives, false negatives, confidence calibration, latency, and user correction rate.
- Test model loading failure, unsupported hardware, memory pressure, cancellation, and concurrent requests.
- Run camera and real-time scenarios on physical devices; simulator image tests are not camera proof.
- Version model assets and keep the evaluation set stable enough to detect regressions.

## Reviewable visual-intelligence contract

Treat every visual output as a proposal until the product’s validation policy promotes it to confirmed data:

`capture -> observation/prediction -> normalization -> confidence/provenance -> review -> confirmed record -> optional enrichment`

| Stage | Owns | Does not own |
| --- | --- | --- |
| Capture | Photo/video/document selection, camera permission, orientation, source reference | Truth of the extracted value |
| Observation/prediction | Vision observation, Core ML output, confidence, geometry, model/revision | User intent, identity, authorization, or durable business state |
| Normalization | Parsing dates/numbers/units, format checks, field mapping | Silent correction of ambiguous text |
| Review | Editable draft, source display, correction, accept/reject, provenance | Re-running every pipeline stage on each keystroke |
| Confirmed record | Durable domain model and audit/provenance policy | Automatic claims beyond the evidence |
| Optional enrichment | Bounded Foundation Models summary or categorization from validated fields | Inventing missing fields or replacing deterministic validation |

Keep confidence and source location when they affect review. A high confidence score is not a guarantee of truth; it is one signal for deciding which fields need attention. If a field is ambiguous, show the source text or image region and let the person correct it.

## Vision request selection

Select the narrowest request that matches the output:

| Output | Route | Design consequence |
| --- | --- | --- |
| Text and bounding boxes | `RecognizeTextRequest` or the current Vision text route | Preserve transcript, confidence, language, and normalized geometry for review |
| Document structure | `RecognizeDocumentsRequest` or document capture route | Use structure as a proposal; validate field meaning and page completeness |
| Barcodes | `DetectBarcodesRequest` or VisionKit scanner | Validate symbology/payload before opening URLs or changing records |
| Foreground/subject mask | Foreground instance mask request | Treat the mask as an image observation, not an identity or ownership claim |
| Custom classification/detection | Core ML model wrapper or `MLModel` | Version the model asset and score false positives/negatives on representative devices |

Prefer the current Swift-native Vision request APIs when they express the target route, but re-check the deployment target and request revision in Xcode. Older `VN*` request examples may still be useful for existing targets, yet they should not silently become the default for an iOS 26 project.

## Live camera and backpressure

Real-time capture creates a rate problem: camera frames can arrive faster than an observation or prediction can complete. Define a policy before connecting the pipeline:

- process the latest frame and drop intermediate frames when the UI only needs current guidance;
- process every frame only when the product can prove the latency, energy, and thermal cost;
- serialize model access when the model or device resources require it;
- cancel in-flight work when the capture flow ends or a new source supersedes it;
- throttle UI updates separately from recognition work;
- preserve the last confirmed result and label it as stale when processing pauses.

Do not make the preview depend on a synchronous, unbounded model call. A smooth camera surface with delayed or stale observations is better than a blocked preview, provided the status and freshness are visible.

## Core ML loading and device policy

For a bundled model, prefer the generated wrapper when it makes inputs and outputs clear. Use `MLModel` directly for downloaded/compiled assets or lower-level configuration. Record the model version, input/output description, compute-unit choice, load time, prediction time, memory pressure, and thermal observations in the evaluation fixture.

Model availability is not equivalent to model quality. A prediction route still needs a fallback, a validation policy, and a device matrix. If the model cannot load or the selected device is too constrained, keep manual entry or a narrower deterministic route available.

## Privacy and retention choices

- Prefer Photos picker selection over broad photo-library access when the feature only needs user-selected assets.
- Keep raw images, transcripts, and embeddings on device unless an upload is necessary, disclosed, and consented.
- Crop or redact regions before passing an image or transcript into another model route.
- Store the minimum source/provenance needed for correction and audit; provide deletion behavior for the source and derived data.
- Do not put health, financial, identity, or private document content into logs by default.
- If validated observations are passed to Foundation Models, pass only the fields needed for the bounded task and keep the model output reviewable.

## Evidence matrix

| Evidence | Proves | Does not prove |
| --- | --- | --- |
| Unit fixture | Parsing, normalization, confidence thresholds, state reduction | Camera focus, real lighting, model availability, or device throughput |
| Image-file test | Vision request behavior for supplied files and orientations | Live camera lifecycle, permission, thermal behavior, or real-time backpressure |
| Preview/UI test | Review form, correction, error, empty, and permission presentation | Hardware capture, neural engine performance, or system camera UI |
| Simulator | Deterministic imported images, navigation, and manual fallback | Physical camera, sensors, actual model/device availability, or thermal behavior |
| Physical device | Camera, focus, lighting, frame pacing, model load/prediction, memory and thermal spot checks | All supported devices, production data, or App Store review |

Never promote a Vision observation or Core ML prediction to a durable fact in a demo path without a review/validation decision recorded in the product contract.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml/)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [Integrating a Core ML model into your app](https://developer.apple.com/documentation/coreml/integrating-a-core-ml-model-into-your-app)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Recognizing text in images](https://developer.apple.com/documentation/vision/recognizing-text-in-images)
- [VisionKit](https://developer.apple.com/documentation/visionkit)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
