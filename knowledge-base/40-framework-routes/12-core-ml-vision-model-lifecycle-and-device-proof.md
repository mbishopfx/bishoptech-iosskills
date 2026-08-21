# Core ML and Vision Model Lifecycle and Device Proof

Core ML and Vision are narrower, more deterministic on-device intelligence routes than a general language model. They are often the right first choice for classification, detection, OCR, geometry, feature extraction, or other bounded image tasks. Foundation Models can enrich or explain a reviewed observation, but it should not replace the model/input/observation contract.

## Route selection

| User outcome | First route | Add only when needed |
| --- | --- | --- |
| Classify a photo or frame | Core ML model with Vision or direct Core ML prediction | Foundation Models for a bounded explanation or draft after validation. |
| Locate objects/text/faces/barcodes | Vision request and observation types | Core ML custom request when the built-in task is insufficient. |
| Predict a custom numeric/category value | Core ML model and generated wrapper or `MLModel` | Vision for image preprocessing/observation integration. |
| Process a live camera stream | AVFoundation capture + bounded Vision/Core ML cadence | SwiftUI review UI, persistence, or Foundation Models after a user-selected frame. |
| Analyze a still image | `ImageRequestHandler`/`VNImageRequestHandler` with one or more requests | Domain validation and user review. |

Do not add a generative model just because the UI needs natural-language copy. Use deterministic labels, formatter logic, or a reviewed template when the task is known and bounded.

## Model asset states

Keep model asset lifecycle separate from prediction state:

```text
bundled source/model
 -> compiled model asset
 -> load/configure
 -> ready
 -> predict
 -> validate observation
 -> review/accept
```

For a model bundled with the app, Xcode can provide a generated wrapper. For downloaded or dynamically compiled models, the app must manage the model URL, compilation, storage, version, integrity, replacement, deletion, and failure path. `MLModel.load(contentsOf:configuration:)` is an asynchronous route for a compiled asset; it does not prove that the model is appropriate for the current input or device workload.

Record:

- model identifier, revision, and source/license decision;
- `.mlmodelc` or downloaded asset version and integrity metadata;
- input/output feature descriptions and image orientation policy;
- `MLModelConfiguration` and selected `MLComputeUnits`;
- model load time, prediction latency, memory, thermal, and battery notes;
- supported device/OS range and fallback when the asset cannot load;
- whether the result is a transient observation, proposal, or accepted domain value.

## Compute-unit choice is a performance experiment

`MLModelConfiguration.computeUnits` selects the processing-unit configuration available to the model. Do not promise that a model uses a particular Neural Engine/GPU/CPU path or that one choice is fastest across devices. Measure the named model, input shape, device, OS, warm/cold state, and workload.

Useful comparison rows:

| Configuration | Measure | Decision boundary |
| --- | --- | --- |
| `.all` or default route | Latency, memory, energy, thermal behavior | General candidate; not a universal best choice. |
| CPU-only route | Predictability and fallback behavior | May be slower; useful for unsupported accelerator paths. |
| GPU/CPU constrained route | Compatibility and energy profile | Device/model-specific; verify actual output and performance. |

Keep model configuration in the evidence record. A simulator’s accelerated execution environment is not equivalent to the target iPhone’s hardware.

## Vision request contract

For an image request, define all of these before implementation:

| Input decision | Required rule |
| --- | --- |
| Source | User-selected still, camera pixel buffer, video frame, or file URL. |
| Orientation | Carry the source orientation into the request handler and model preprocessing. |
| Crop/scale | Choose the documented crop/scale policy; do not silently distort the source. |
| Request/revision | Select the API revision supported by the target SDK and model. |
| Output | Observation type, confidence semantics, geometry coordinate space, and provenance. |
| Cadence | For live input, maximum inference frequency, dropped-frame policy, and stale-result behavior. |
| Acceptance | Deterministic thresholds, duplicate handling, review/edit path, and domain commit rule. |

`VNCoreMLRequest` forwards Core ML confidence values as supplied; it does not normalize every confidence into a universal `[0, 1]` meaning. Do not compare confidence values across unrelated models or present them as calibrated probabilities without an evaluation that supports that claim.

Apple’s current Vision framework also exposes Swift-only request/handler APIs. Choose the modern or legacy route intentionally, confirm the deployment target, and avoid mixing observation types or completion/cancellation assumptions from different API generations.

## Live capture pipeline

Keep camera delivery, inference, rendering, and accepted data on separate boundaries:

```text
AVCaptureSession / preview
  -> bounded frame queue
  -> Vision/Core ML request
  -> observation + timestamp + source revision
  -> UI overlay or proposal
  -> person selects/approves
  -> domain record
```

For `AVCaptureVideoDataOutput`, decide whether late frames are discarded. If the inference queue blocks, retaining every old frame can increase memory and make the UI show stale information. A bounded, latest-frame policy is often preferable for a live preview, but the product must label freshness and choose an appropriate cadence for the user outcome.

Configure `AVCaptureSession` on its session queue, use `beginConfiguration()`/`commitConfiguration()` for grouped changes, and do not call blocking `startRunning()` on the main actor. Camera/microphone authorization, interruptions, route changes, session failure, and teardown are part of the feature state.

## Observation versus domain truth

Use an explicit boundary:

```text
pixel buffer/photo
  -> Vision/Core ML observation
  -> deterministic normalization and validation
  -> optional Foundation Models proposal
  -> user review
  -> canonical domain record
```

An observation can be stale, wrong, partial, or outside the supported model distribution. It is not an identity, permission, measurement, medical conclusion, purchase, or completed action. Preserve source provenance and allow the person to correct or reject it.

## Foundation Models enrichment boundary

Foundation Models can help turn reviewed visual observations into a concise description, organize fields, or draft a user-facing note. Keep the model input small and source-linked:

- pass structured observations and source references, not an unbounded camera history;
- distinguish observed values from generated explanation;
- validate dates, identifiers, quantities, authorization, and policy deterministically;
- review before writing records or invoking an App Intent/system surface;
- keep a manual path when the language model is unavailable or refuses.

Do not use a language model to “fix” an uncertain visual observation without showing the uncertainty and preserving the source.

## Device and model proof

| Claim | Minimum evidence |
| --- | --- |
| Model API is usable | Official source, target SDK, model asset/wrapper, compile result. |
| Model loads | Named model asset/version, configuration, load success/failure, device/OS. |
| Prediction is useful | Representative/negative/ambiguous fixtures, model revision, orientation/crop, field-level evaluation. |
| Live inference is responsive | Physical device, frame cadence/drops, latency, memory, thermal, battery, and stale-result policy. |
| Confidence is meaningful | Calibration/threshold evaluation for the named model and task; never infer from one demo. |
| Camera route is shippable | Physical camera permission, interruption, orientation, lock/termination/relaunch, privacy copy, and release target evidence. |
| AI enrichment is safe | Source/provenance, prompt/schema/tool version, refusal/fallback, deterministic validation, user review, and commit result. |

Simulator tests can cover deterministic image fixtures and UI branches. They do not prove camera access, model accelerator behavior, physical frame timing, thermal/battery behavior, or the user’s real lighting/angle/background conditions.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModel.load(contentsOf:configuration:)](https://developer.apple.com/documentation/coreml/mlmodel/load%28contentsof%3Aconfiguration%3A%29)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLComputeUnits](https://developer.apple.com/documentation/coreml/mlcomputeunits)
- [Integrating a Core ML model into your app](https://developer.apple.com/documentation/coreml/integrating-a-core-ml-model-into-your-app)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [Classifying images with Vision and Core ML](https://developer.apple.com/documentation/coreml/classifying-images-with-vision-and-core-ml)
- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [AVCaptureVideoDataOutput](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput)
- [alwaysDiscardsLateVideoFrames](https://developer.apple.com/documentation/avfoundation/avcapturevideodataoutput/alwaysdiscardslatevideoframes)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
