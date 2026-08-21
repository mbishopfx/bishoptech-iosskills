# SwiftUI MLTensor, Metal, and Accelerate on-device compute design

This design route is for a native app that uses tensor math, camera/pixel-buffer processing, custom GPU work, or explicit CPU/ML/GPU compute policy. It pairs with the [on-device compute review](../42-framework-deep-dives/116-swiftui-mltensor-metal-accelerate-on-device-compute-review.md), the [route](../50-capability-recipes/147-swiftui-mltensor-metal-accelerate-on-device-compute-review-route.md), the [proof matrix](../60-verification/141-swiftui-mltensor-metal-accelerate-on-device-compute-proof-matrix.md), and the [recipes](../70-code-recipes/159-swiftui-mltensor-metal-accelerate-on-device-compute-review-recipes.md).

The design should make an advanced compute pipeline feel like a calm native app. People need a source, a visible task, a current result, a safe next action, and a recoverable fallback. They do not need an unexplained “GPU mode” badge or a wall of tensor dimensions.

## 1. Start with the product task

Use one of these task shapes:

- **Transform** — resize, filter, enhance, or convert a photo/video frame;
- **Observe** — show a transient camera or sensor-derived state;
- **Analyze** — produce a reviewable score, feature, classification, or measurement;
- **Generate** — create a candidate from tensor/model output;
- **Compose** — combine a model with a custom Metal/BNNS/MPSGraph operation;
- **Inspect** — give an advanced person visibility into device, shape, timing, or memory state.

The UI contract should read:

```text
input -> preparing -> processing -> result -> review/approval -> saved or discarded
```

Low-level compute remains invisible to the domain model. A tensor result becomes a user-facing proposal only through an app-owned adapter and validation policy.

## 2. Use a native hierarchy

Recommended shell:

1. **Source** — photo, camera preview, document, or generated fixture;
2. **Task** — one clear transform/analyze/generate action;
3. **Status** — preparing/running/paused/constrained/complete;
4. **Result** — image, text, measurement, or candidate record;
5. **Details** — optional input shape, device policy, timing, and memory disclosure;
6. **Actions** — retry, cancel, save, undo, fallback, or manual edit.

Use standard SwiftUI controls and navigation. Place advanced tensor/Metal details in an inspector sheet, disclosure group, or diagnostics destination rather than inside the primary task.

## 3. Design a source surface that tells the truth

For camera and media:

- show the current image/frame and its freshness;
- label paused, stale, processing, and accepted states;
- preserve orientation and crop context when it affects the result;
- make capture/confirm explicit before durable use;
- keep source permissions and interruptions recoverable.

For an imported image or document:

- show the selected source and change affordance;
- disclose if the pipeline uses a crop, downscale, or color conversion;
- preserve the original when a computed result is only a candidate;
- allow a manual path when compute is constrained.

Do not use a blurred overlay to hide that the current frame is stale or that a command buffer has not completed.

## 4. Make preparation and compute states legible

Use a simple state language:

| State | Design meaning |
| --- | --- |
| Ready | The selected input and compute route can accept work |
| Preparing | Tensor/graph/pipeline/resources are being created |
| Running | Work has been admitted and is in flight |
| Waiting | The route is queued behind a bounded resource policy |
| Paused | Camera/app/permission/thermal state prevents progress |
| Constrained | A lower-power or fallback route is active |
| Stale | A result no longer belongs to the visible source/task |
| Complete | A result exists and is ready for review |
| Failed | The app has an actionable error and can preserve the source |

If the app cannot provide real percentage progress, use honest indeterminate progress with a cancel action. Do not display “Neural Engine” or “zero-copy” as if they were visible user outcomes.

## 5. Glass roles for compute controls

Liquid Glass works best for compact, floating controls in context:

- camera capture/pause/stop controls;
- a small processing status capsule;
- retry/fallback/cancel actions;
- a compact source/task switcher;
- an inspector toolbar for advanced users.

Keep the main result, model/source explanation, warnings, and dense details on stable high-contrast surfaces. Avoid nested translucent cards, continuously morphing shapes, and decorative blur behind numbers that must be read.

Use system controls first. If a custom Liquid Glass effect is added, verify contrast, reduced transparency, reduced motion, Dynamic Type, VoiceOver, pointer, keyboard, and Switch Control. Glass should remain optional to functionality.

## 6. Result design by task

### Transform

Show before/after or original/derived imagery, preserve the original, and disclose any resolution/format change. A Save or Replace action requires a deliberate review step.

### Observe

Show the current value plus last-updated time/frame, and distinguish transient display from a saved event. Avoid a constantly moving UI that prevents VoiceOver or keyboard users from understanding the state.

### Analyze

Show the result with method/source/model/compute provenance where useful. Treat thresholds as app policy, not as a framework guarantee. Give a reason when validation blocks Save.

### Generate

Show a candidate/draft state, warnings, and editable content. Separate generation from tool/domain commands and make approval explicit.

### Inspect

Use a graph/tensor/metrics screen for advanced users. Provide a text summary, accessible labels, and copy/export of redacted evidence. A chart of elapsed time must not be presented as a universal benchmark.

## 7. Device and policy disclosure

Use plain language in the primary UI:

- “Automatic”;
- “Lower power”;
- “High performance”;
- “Using fallback.”

In advanced details, show:

- tensor shape/rank/scalar type;
- input/output format and storage path;
- selected `MLComputePolicy`/Metal resource policy;
- actual device class and OS;
- queue/operation status;
- measured elapsed time and memory sample;
- whether the metric is estimated, observed, or cached.

Never claim “runs on the Neural Engine” from a CPU/GPU tensor policy. Never claim “zero-copy” without naming the specific buffer/texture path and measurement.

## 8. Accessibility task design

The route must support:

1. choosing or capturing a source;
2. understanding permission and source orientation/state;
3. starting, pausing, and cancelling work;
4. understanding that work is in progress or constrained;
5. reviewing a result and its freshness/provenance;
6. editing/approving/saving or discarding a candidate;
7. recovering through fallback or manual processing.

Use semantic labels and values, not raw tensor names. Announce meaningful transitions without producing a constant stream of frame-level updates. Provide non-gesture alternatives for capture, cancel, disclosure, and save.

## 9. Privacy and sensitive compute states

If the source is a camera frame, face, document, health signal, or private image, the UI should state:

- whether processing is on device;
- whether frames are retained or discarded after processing;
- whether any result or diagnostics leave the device;
- how the person can delete derived output;
- whether a low-level debug/metrics route is disabled in production.

Do not render raw intermediate tensors by default. If an inspector is necessary, use explicit opt-in and redaction.

## 10. Layout across devices

On iPhone, prioritize source/result and one primary action. On iPad/Mac, use a split or inspector layout for source, result, and diagnostics. In landscape camera use, keep controls near reachable edges and avoid covering the subject. On smaller sizes, move advanced details into a sheet rather than shrinking text below readable sizes.

The compute engine should not dictate the UI layout. The same state model can feed a phone review screen, an iPad workspace, and a Mac diagnostics view.

## 11. Acceptance matrix

| Design area | Acceptance question |
| --- | --- |
| Native shell | Does the screen look and behave like a platform app before custom compute is visible? |
| Source | Can a person tell which image/frame/data is being processed? |
| Status | Are preparing/running/paused/stale/constrained states honest? |
| Result | Is the output visibly a candidate or a committed record? |
| Controls | Can cancel/retry/fallback/save/undo be reached semantically? |
| Glass | Does material help grouping without reducing legibility? |
| Details | Are estimates, measurements, and target claims labeled accurately? |
| Privacy | Does copy match retention and data path? |
| Accessibility | Can the same task be completed with assistive input? |
| Release | Does the signed build demonstrate the exact compute path and fallback? |

## Stop conditions

Reject the design when a GPU/tensor state is represented only by an animation, when a result can be saved before completion/validation, when the source/frame is not identifiable, when a fallback is hidden, when glass or motion prevents accessibility, or when performance copy is based on an unqualified benchmark.

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLTensor](https://developer.apple.com/documentation/coreml/mltensor)
- [MLComputePolicy](https://developer.apple.com/documentation/coreml/mlcomputepolicy)
- [Accelerate](https://developer.apple.com/documentation/accelerate)
- [BNNS](https://developer.apple.com/documentation/accelerate/bnns-library)
- [Metal](https://developer.apple.com/documentation/metal)
- [MTLBuffer](https://developer.apple.com/documentation/metal/mtlbuffer)
- [MTLTexture](https://developer.apple.com/documentation/metal/mtltexture)
- [MTLCommandBuffer](https://developer.apple.com/documentation/metal/mtlcommandbuffer)
- [Setting resource storage modes](https://developer.apple.com/documentation/metal/setting-resource-storage-modes)
- [Metal Performance Shaders Graph](https://developer.apple.com/documentation/metalperformanceshadersgraph)
- [MPSGraph](https://developer.apple.com/documentation/metalperformanceshadersgraph/mpsgraph)
- [CVMetalTextureCacheCreateTextureFromImage](https://developer.apple.com/documentation/corevideo/cvmetaltexturecachecreatetexturefromimage%28_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A_%3A%29?changes=_3_2&language=objc)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
