# Core ML reviewable inference and native Liquid Glass design

## Design goal

An Apple-native AI surface should make three things obvious at a glance: what the app observed, what the model suggested, and what the person can decide. Use Core ML for local inference, SwiftUI for adaptive presentation, and Liquid Glass for lightweight grouping. The result should feel native because the hierarchy, controls, motion, typography, and accessibility are coherent—not because the screen copies an Apple product.

The design contract is:

`source -> model state -> suggestion -> evidence -> user decision -> domain result`

## State model before styling

Design model lifecycle states before choosing a material:

| State | User-facing meaning | Safe action |
| --- | --- | --- |
| Bundled | The app includes the model asset | Inspect model status or run when inputs are valid. |
| Downloading | A model package is being fetched | Cancel/retry; use a deterministic fallback. |
| Compiling | Core ML is preparing a local compiled asset | Keep the task resumable and avoid implying readiness. |
| Validating | Schema, version, and fixture checks are running | Show that the model is not yet active. |
| Ready | The model passed local readiness checks | Run prediction or let the person choose. |
| Predicting | A bounded inference is in flight | Show progress only when useful; avoid unbounded live spinners. |
| Needs review | A typed suggestion exists | Edit, accept, reject, or inspect the source. |
| Unavailable | The model or input capability cannot run | Use a fallback or explain the missing requirement. |
| Failed | A load, contract, or prediction step failed | Preserve the source; offer retry or remove the model. |
| Updating | Personalization or asset replacement is in progress | Keep the previous known-good model until promotion. |

Avoid one generic `isLoading` flag. A model can be loaded while the camera is unavailable, a prediction can be complete while the source is stale, and a model can be present while its contract is incompatible.

## A review card anatomy

Use a compact, readable structure:

```text
source thumbnail / input summary
  model name · version · local status
  suggested result or “not enough evidence”
  evidence / source IDs / timestamp
  [Edit] [Accept] [Reject] [Run again]
```

The source line should identify what the result came from without exposing sensitive content unnecessarily. “Suggested” and “detected candidate” are safer defaults than declarative language when the model is not a verified domain authority. If the model exposes a score, label it in plain language and avoid implying calibrated probability unless the product has actually established that.

When a proposal changes durable data, show the before/after diff. For destructive or external actions, require a separate confirmation that names the exact effect. Never bury the side effect in a glass button labeled only “Continue.”

## Liquid Glass rules for model UI

Liquid Glass works best as a compact control or status layer over the real content. Keep the input media or source record visually primary. Use native controls and materials where possible, then add a glass group for:

- model status and source provenance;
- a small set of review actions;
- filters or display settings;
- an explicit “use local model” or “download model” choice;
- a compact result summary that can expand into detail.

Avoid a full-screen translucent panel that makes a model output look authoritative. Glass should not obscure the source, hide loading/error state, or force a person to remember whether a result was accepted. When the system reduces transparency or increases contrast, the structure must remain understandable without blur.

Use native transitions for state changes: status text can update in place, a result can appear after a bounded operation, and a review sheet can present the full evidence. Motion should communicate “new result,” “replaced model,” or “needs attention,” not simulate intelligence.

## Layout and information hierarchy

Prefer a three-level hierarchy:

1. **Primary task** — capture, select, or review the source.
2. **Model observation** — show the result and its state.
3. **Decision** — edit, accept, reject, retry, or use a fallback.

On compact width, use a list/detail or bottom-sheet route instead of compressing every field into a toolbar. On larger widths, keep the source and review detail side by side when it reduces navigation cost. Preserve the same domain state across size classes; only the presentation changes.

Do not make a color gradient, confidence ring, or animated particle the only indicator of uncertainty. Use text, value, and action labels. A model with no result should have a clear empty or unavailable state, not a blank glass card.

## Accessibility and input

The review flow must be completable without seeing the source image or performing a drag gesture. Give every control an accessible label, value, hint where helpful, and action. Expose model state as a stable status element, then move focus deliberately to the result or first review action only when that helps the task.

Test:

- VoiceOver reading order from source to model status to decision;
- Dynamic Type with long labels, version strings, and localized errors;
- Voice Control names for model actions;
- Switch Control and keyboard/pointer equivalents;
- increased contrast and reduced transparency;
- reduced motion while the model changes state;
- right-to-left layout and pluralized source/result counts.

Do not use confidence color, icon shape, or animation as the only state channel. Keep the same review action available in the accessible detail route and the compact glass control group.

## Privacy and trust language

“On device” is a useful implementation fact, not a complete privacy promise. State what is processed, what is retained, whether a model is downloaded, and what happens when the person deletes the source. Avoid marketing language that turns a model score into a claim about a person.

For sensitive inputs, show provenance and retention near the action that creates the output. If the feature can run without network access, say that only when the implementation and fallback behavior are verified. If a downloaded model is optional, make the download size, version, and removal route discoverable.

## Design acceptance checklist

| Question | Pass condition |
| --- | --- |
| Is the source visible? | The person can inspect what the model saw or the source record that produced the output. |
| Is the model state distinct from result state? | Downloading, compiling, validating, unavailable, and failed are not collapsed into “loading.” |
| Is uncertainty legible? | A score or model label is not styled as a verified fact without evidence. |
| Is the action reversible? | Reject/edit/reset paths exist before durable or external side effects. |
| Is the shell adaptive? | Dynamic Type, dark mode, increased contrast, reduced transparency, and compact width retain hierarchy. |
| Is the route accessible? | VoiceOver, keyboard, pointer, Switch Control, and Voice Control can complete the task. |
| Is privacy understandable? | Input, retention, download, and deletion behavior are explained at the relevant decision point. |
| Is the visual claim honest? | A screenshot cannot be the only proof of runtime, quality, latency, or privacy. |

## Sources

- [Core ML](https://developer.apple.com/documentation/coreml)
- [MLModel](https://developer.apple.com/documentation/coreml/mlmodel)
- [MLModelConfiguration](https://developer.apple.com/documentation/coreml/mlmodelconfiguration)
- [MLModelDescription](https://developer.apple.com/documentation/coreml/mlmodeldescription)
- [MLFeatureValue](https://developer.apple.com/documentation/coreml/mlfeaturevalue)
- [MLFeatureProvider](https://developer.apple.com/documentation/coreml/mlfeatureprovider)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion)
