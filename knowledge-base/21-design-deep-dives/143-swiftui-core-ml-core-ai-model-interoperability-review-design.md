# SwiftUI Core ML and Core AI model-interoperability design

This design route is for apps that accept a photo, camera stream, document, or structured input; choose or deliver a model; produce a Core ML/Vision/Core AI result; and ask a person to review a proposal. It pairs with the [model-interoperability review](../42-framework-deep-dives/115-swiftui-core-ml-core-ai-model-interoperability-review.md), the [implementation route](../50-capability-recipes/146-swiftui-core-ml-core-ai-model-interoperability-review-route.md), the [proof matrix](../60-verification/140-swiftui-core-ml-core-ai-model-interoperability-proof-matrix.md), and the [code recipes](../70-code-recipes/158-swiftui-core-ml-core-ai-model-interoperability-review-recipes.md).

The visual goal is Apple-native clarity: the person should understand the source, model lane, preparation state, result provenance, uncertainty, and next action without seeing framework names as product copy. Core ML and Core AI may share a review shell, but they do not share an artifact or availability contract.

## 1. Design the user outcome first

Write the outcome as a reviewable task:

```text
source -> model preparation -> observation/prediction -> candidate -> validation -> approval -> commit
```

Examples:

- classify a selected photo and save a user-approved tag;
- detect a document region and offer a crop, without silently overwriting the original;
- observe a live camera frame and show a transient hint, without storing every frame;
- personalize an updatable model, with an explicit private-training state and rollback;
- choose a Core ML or Core AI lane, while preserving a deterministic iOS 26 route.

The primary screen should never imply that model output is a final record before validation and approval.

## 2. Use a native workspace shell

Prefer standard SwiftUI navigation, `NavigationStack`, `ToolbarItem`, `List`, `Form`, `ScrollView`, `ContentUnavailableView`, sheets, alerts, and semantic controls. A useful information architecture is:

1. **Source** — selected photo, camera state, document, or structured input.
2. **Model** — name, revision, runtime lane, readiness, and delivery status.
3. **Inspect** — preprocessing, crop/scale/orientation, input constraints, and optional compute plan.
4. **Observe** — live frame or single-image result with freshness and request identity.
5. **Review** — candidate values, confidence/quality notes, source provenance, and warnings.
6. **Apply** — validation, user approval, deterministic command, undo, and rollback.

Use a split view or bottom bar only when the device size class and task justify it. Do not turn a small iPhone screen into a developer console merely because a model has tensors.

## 3. Model identity is visible but calm

The model card should show:

- human-readable model name;
- source/model revision;
- Core ML, Vision, Core AI, or deterministic lane;
- bundled/downloaded/prepared state;
- input type and preprocessing summary;
- last update/check time when relevant;
- privacy/data-path statement;
- fallback availability.

Use a secondary disclosure for digest, compiler/toolchain, compute policy, and artifact details. A digest is evidence for reproducibility, not useful headline copy for every person.

## 4. Source selection and provenance

The source card must distinguish:

| State | Person-facing meaning |
| --- | --- |
| No source | Choose a photo, allow camera, or enter data |
| Permission needed | The app is waiting for a system permission decision |
| Source selected | The app has a specific image/document/frame to analyze |
| Source changed | The prior candidate may no longer describe the visible source |
| Live source | The result is tied to a frame/time and may become stale |
| Source unavailable | The app offers a picker, retry, or deterministic path |

Expose orientation/crop changes when they can materially affect a result. Avoid showing a model prediction detached from the thumbnail, frame timestamp, or source label that produced it.

## 5. Preparation states are first-class

Preparation can include model download, verification, compilation, Core AI specialization, cache lookup, Vision request construction, or camera authorization. Use a state model such as:

```text
unsupported -> permission -> downloading -> verifying -> compiling/specializing
    -> ready -> observing/running -> needs review -> applied
    -> failed/retry/fallback
```

The progress surface should answer:

- what is happening;
- whether the user can cancel;
- whether data stays on device;
- whether the app can continue with a fallback;
- what will remain if preparation fails.

Never label a model “ready” when only the file exists but compilation, specialization, input compatibility, or the selected device lane remains unproven.

## 6. Compute policy is a detail with a consequence

For most people, “automatic” or “best available on this device” is a better label than CPU/GPU/Neural Engine jargon. In an advanced inspector, show the selected Core ML `computeUnits` policy and any Core AI target profile as explanatory details.

If a policy changes battery, thermal, background, or latency behavior, describe the consequence. Do not present a device-compute icon as a promise of real-time performance.

`MLComputePlan` information can support an expert disclosure about anticipated operation cost/device use. The UI must label it as an estimate, not as an observed runtime trace.

## 7. Single-image review

For a single image:

- keep the source preview visible beside or above the result;
- show crop/scale mode if the model does not see the full image;
- place candidate values in editable, semantic controls;
- show confidence or quality only with an explanation and calibration policy;
- make “use this” a review action, not an immediate destructive save;
- allow retry with a different model or manual entry;
- preserve the original source and draft if the model fails.

If Vision returns classifications, boxes, masks, or feature-value observations, map them into user concepts in the app layer. Framework observation types should not leak into customer-facing copy.

## 8. Live camera and sequence review

For a live route:

- show a clear capture/analysis indicator;
- distinguish the current frame from the last accepted observation;
- show “paused,” “processing,” and “stale” states without relying on color alone;
- throttle or sample frame work so the UI remains responsive;
- provide an explicit capture/confirm action before durable change;
- allow the person to stop the camera and keep the last reviewable frame;
- design interruption, backgrounding, denied access, and unsupported device states.

Avoid permanent overlays that obscure the camera subject or imply that every transient prediction is a verified fact.

## 9. Downloaded and updated model design

The model library should show:

- which model is installed or available;
- download/verification/compilation progress;
- storage footprint and removal affordance;
- source revision and compatibility range;
- whether the model is a shared baseline or private personalization;
- update/revert behavior;
- offline behavior.

An update should be staged, checked, and activated. The prior accepted model should remain available until the new model passes its acceptance fixtures. Avoid silent model changes that make past results incomparable.

## 10. Core ML/Core AI lane handoff

When the app can use both lanes, give the person a stable product concept such as “On-device model” and reveal the lane only where it affects behavior. If Core AI requires a newer OS/toolchain or target, show a deterministic fallback rather than an empty Core AI panel.

An internal route can be:

```text
Core AI available and accepted -> Core AI artifact
else Core ML artifact available and accepted -> Core ML/Vision route
else -> deterministic/manual route
```

The result card carries a runtime-lane label and model revision for provenance, but review and commit behavior remains consistent.

## 11. Liquid Glass composition

Use Liquid Glass to group a small set of floating controls—source selection, capture, model choice, or review actions—when the surrounding content benefits from material separation. Keep the source image, candidate text, warnings, and large data views on a legible surface.

Good roles:

- compact camera controls over a live surface;
- a model/status capsule with one or two actions;
- a review action group that morphs between “Review,” “Apply,” and “Undo”;
- a navigation or toolbar cluster.

Poor roles:

- entire screens of nested translucent cards;
- low-contrast tensor/debug tables;
- hiding a permission or model-failure state behind decorative material;
- using blur to imply confidence or intelligence.

Respect reduced transparency, increased contrast, reduced motion, Dynamic Type, VoiceOver, pointer, keyboard, and Switch Control. A glass treatment is optional; task comprehension is not.

## 12. Review and validation states

Use a clear distinction between:

- **Candidate** — produced by a model or deterministic recognizer;
- **Validated** — passed app-owned schema/range/source/revision checks;
- **Approved** — explicitly accepted by the person or authorized workflow;
- **Applied** — committed through a deterministic domain command;
- **Rejected/stale** — cannot be applied to the current source or record.

Display the reason for a blocked Apply action. “Low confidence” is not enough if the actual blocker is a mismatched source revision, invalid shape, unavailable model, changed record, or missing permission.

## 13. Accessibility and alternate input

Test tasks, not just visuals:

1. choose a source and identify it;
2. grant or deny camera/photo permission and recover;
3. understand model lane, revision, and readiness;
4. start, pause, and cancel analysis;
5. understand that a result is a candidate;
6. inspect warnings and validation failure;
7. edit or reject a candidate;
8. approve, apply, undo, or use a fallback.

Provide accessibility labels that include state and provenance. Ensure a person can perform the route with VoiceOver, Dynamic Type, increased contrast, reduced transparency, reduced motion, keyboard/Full Keyboard Access, Switch Control, and pointer input. Do not rely on red/green overlays, camera gestures, or a glass blur to communicate state.

## 14. Design acceptance matrix

| Area | Acceptance question |
| --- | --- |
| Native shell | Does the app use standard hierarchy, controls, typography, safe areas, and platform navigation? |
| Source trust | Can a person tell what image/frame/data produced the candidate? |
| Model trust | Can a person identify model lane/revision and know when it is not ready? |
| Live behavior | Can the person distinguish current, stale, paused, and accepted observations? |
| Review | Is the candidate editable and clearly separate from committed truth? |
| Failure | Does a failed download/compile/load/prediction preserve the source and offer a next action? |
| Glass | Does material improve grouping without harming contrast, reading, or actionability? |
| Accessibility | Can assistive users complete the same outcome? |
| Privacy | Does copy match actual on-device, downloaded, and personalized data paths? |
| Release | Does the shipped archive/TestFlight route match the designed model lane and fallback? |

## Stop conditions

Reject the design when:

- a model card hides the source/revision or uses a generic “AI” badge as proof;
- a live prediction is visually treated as a durable fact;
- the Apply action is reachable before validation and approval;
- a downloaded or personalized model update silently changes the result contract;
- nested glass surfaces reduce contrast or obscure failure/provenance;
- accessibility depends on color, hover, camera gesture, or transparency;
- a Core AI-only screen has no iOS 26 or deterministic fallback;
- the design cannot show why a result is stale, rejected, or unavailable.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelAsset](https://developer.apple.com/documentation/coreml/mlmodelasset)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [computeUnits](https://developer.apple.com/documentation/coreml/mlmodelconfiguration/computeunits)
- [MLComputePlan](https://developer.apple.com/documentation/coreml/mlcomputeplan-1w21n)
- [Model Personalization](https://developer.apple.com/documentation/coreml/model-personalization)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [VNImageRequestHandler](https://developer.apple.com/documentation/vision/vnimagerequesthandler)
- [VNSequenceRequestHandler](https://developer.apple.com/documentation/vision/vnsequencerequesthandler)
- [Classifying Images with Vision and Core ML](https://developer.apple.com/documentation/coreml/classifying-images-with-vision-and-core-ml)
- [Core AI](https://developer.apple.com/documentation/coreai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
