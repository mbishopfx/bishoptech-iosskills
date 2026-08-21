# SwiftUI Core AI on-device model-runtime review design

Core AI is an execution capability, not a visual identity. The design job is to make model readiness, data path, latency, uncertainty, source provenance, and approval legible while the surrounding app still feels like a native Apple platform experience.

This page pairs with the [Core AI runtime review](../42-framework-deep-dives/113-swiftui-core-ai-on-device-model-runtime-review.md), the [Core AI route](../50-capability-recipes/144-swiftui-core-ai-on-device-model-runtime-review-route.md), and the [Core AI proof matrix](../60-verification/138-swiftui-core-ai-on-device-model-runtime-proof-matrix.md).

## Version-aware product shape

The current Core AI integration article documents iOS 27, macOS 27, and Xcode 27 or later. Foundation Models LanguageModelSession is available on iOS 26, but the custom LanguageModel bridge and Core AI provider route are documented for iOS 27. Design the product as one coherent experience with explicit capability lanes:

| Runtime | User-visible experience | Design rule |
| --- | --- | --- |
| iOS 26 supported route | The feature works with the system model, Core ML, Vision, Metal, or deterministic code when available | Do not show a disabled Core AI control as the primary experience |
| iOS 26 unavailable route | Manual or deterministic workflow with a concise explanation | Preserve the user’s source and next action |
| iOS 27 Core AI direct route | Custom on-device model status, preparation, inference, and review | Show that the result is generated locally, but do not imply correctness |
| iOS 27 Core AI Foundation Models route | Familiar session UI backed by the selected provider | Expose provider capabilities and data path when they affect trust |
| Downloading or updating | Asset transfer and integrity state | Never present an unverified model as ready |
| Thermal or memory constrained | Deferred or reduced-quality route | Explain the action and offer a safe fallback |

Do not use the same visual badge for “file exists,” “model loaded,” “inference succeeded,” and “domain accepted.” Those are different states.

## The native shell

Use a normal SwiftUI hierarchy first:

1. navigation title or feature title;
2. source or task context;
3. result or review content;
4. compact status area;
5. primary action and secondary fallback;
6. privacy, model, and revision details where they matter.

Use Liquid Glass as a material for functional controls and status grouping, not as a decorative wrapper around every view. The system should remain readable when transparency is reduced, contrast is increased, text is enlarged, or motion is reduced.

### Glass roles

| Role | Suitable glass treatment | Avoid |
| --- | --- | --- |
| Primary action | A prominent system button or control with a clear label and adequate hit target | A floating icon whose meaning depends on a generated glow |
| Runtime status | A compact glass group containing state, route, and progress | A persistent “AI is thinking” ornament with no actionable information |
| Review card | A bounded material surface around the proposal, source, and changed fields | A full-screen translucent overlay that hides source evidence |
| Fallback | A normal secondary control or inline message | A disabled glass control that gives no reason |
| Model inventory | A list or inspector with standard rows and disclosure | A fake system settings panel that copies Apple branding |

The visual language can be Apple-like through hierarchy, spacing, typography, controls, and behavior. It should not copy proprietary screens, icons, or branding.

## Model state language

Use app-owned state, not raw framework objects, in SwiftUI. A useful state vocabulary is:

| State | Short label | Detail and action |
| --- | --- | --- |
| unsupported | Later system required | “This on-device model needs iOS 27 or later.” Offer the iOS 26 route |
| unavailable | Model unavailable | Explain whether the device, language, asset, or setting is the blocker |
| sourceMissing | Preparing model | Show download or setup action |
| integrityChecking | Verifying model | Avoid showing a result surface yet |
| specializing | Preparing on this device | Show elapsed/progress text only when measured; allow cancel |
| cacheHit | Ready | Do not over-celebrate a cache hit as quality assurance |
| functionLoading | Loading feature | Keep the task context visible |
| running | Processing | Provide cancel and an accessible status announcement |
| partial | Draft result | Label partial output and prevent accidental commit |
| proposal | Review required | Show source, model, revision, uncertainty, and changes |
| validating | Checking result | Keep commit disabled until deterministic validation finishes |
| accepted | Ready to apply | Require the explicit user action when side effects matter |
| constrained | Temporarily limited | Explain thermal, memory, battery, or concurrency reason |
| failed | Could not complete | Preserve input and show retry/fallback path |

The UI can compress these into a single status row, but the state machine should not.

## A trustworthy result card

A Core AI result card should answer five questions before it asks for a commit:

- What source did the model see?
- Which model and revision produced the result?
- What is the output, and which fields are uncertain or generated?
- What deterministic checks ran?
- What exactly will change if the person taps Apply?

Recommended hierarchy:

    source preview -> generated observation -> validation notes -> changed fields -> Apply / Edit / Retry

If the output is a tensor or segmentation mask, add a domain-specific interpretation layer. Do not label a raw probability as “truth.” If it is an image or media edit, show the original and proposed output with a reversible action.

### Confidence language

Use language that matches evidence:

| Evidence | Better label |
| --- | --- |
| Raw model score | “Model score” |
| Thresholded model output | “Candidate” |
| Cross-checked by deterministic code | “Checked candidate” |
| User accepted | “Approved by you” |
| Persisted domain state | “Saved” |

Avoid “verified” unless the app actually ran the verification that the label implies.

## First-run and latency design

Model loading can include resource loading, compilation, and device specialization. The person should understand why the first run takes longer.

### Preparation surface

Use a short, task-oriented preparation message:

- “Preparing this model on your iPhone.”
- “This can take longer the first time.”
- “You can cancel and use manual entry.”

Show a real progress value only when the underlying operation supplies a trustworthy measurement. Otherwise use an indeterminate progress view with a cancel action.

Do not make a first-run model load happen inside a button with no feedback. Prewarm or specialize during a predictable preparation moment, but keep the feature functional if the person declines.

### Long-running operation

For repeated camera or media inference:

- use a latest-frame policy or bounded queue;
- show when the feature is paused or throttled;
- avoid animating every frame as a visual “AI pulse”;
- keep the UI responsive while the actor or task owns inference;
- cancel when the source disappears or the screen leaves the task.

For a single request, the result area can transition from placeholder to partial to complete. Respect reduced motion by using opacity or content replacement rather than a large morph.

## Source and provenance design

When the input is a photo, frame, document, or audio sample, show enough provenance to let a person identify the source:

- thumbnail or waveform;
- source name or app-owned record label;
- capture or modification date when meaningful;
- orientation/crop indicator for transformed imagery;
- source revision or “edited copy” label;
- privacy route such as On Device or Network required.

For a downloaded model, model provenance can include:

- model display name;
- model revision;
- artifact state;
- storage footprint;
- data path;
- supported OS/device family;
- last successful validation date.

Avoid overwhelming the main screen with implementation details. Put full manifests and digests behind a disclosure view or developer-only diagnostic route.

## Fallback and failure design

Fallback is part of the product, not an error dump. Each failure should answer:

1. What failed: device support, asset, specialization, input, memory, thermal, provider, or validation?
2. What was preserved: source, draft, or previous saved state?
3. What can the person do next: retry, use manual entry, reduce input, download, or switch route?
4. Did any domain mutation occur? Show the answer explicitly.

Examples:

| Failure | User-facing response |
| --- | --- |
| iOS 26 cannot use Core AI | “This custom on-device model is available on iOS 27 or later. You can continue with the built-in route.” |
| AOT architecture missing | “This model package does not include a version for this device. Download the supported package or use the fallback.” |
| Memory pressure | “The model needs more memory right now. Try a smaller image or manual mode.” |
| Thermal constraint | “Processing is paused while the device cools.” |
| Descriptor mismatch | “This model update is not compatible with this app version.” |
| Inference cancellation | “Nothing was saved.” |
| Validation rejected | “The model suggestion did not pass the app’s checks. Review or enter it manually.” |

Never imply that an offline failure was a privacy failure or that a provider failure was a model-quality result.

## Model inventory and diagnostic views

A model-management view is useful for power users and support, but it should remain native and sparse. Use sections such as:

### Current route

- On Device or another clearly named path;
- supported OS and device condition;
- availability and readiness;
- current model revision.

### Asset

- bundled or downloaded;
- verified or pending verification;
- size on disk;
- tokenizer/resource status;
- cache status.

### Capabilities

- image input;
- stateful execution;
- guided generation;
- tool calling;
- reasoning;
- exact limitations.

Capabilities should come from the model contract or declared provider capability and be phrased as “supports” rather than “will always do.”

### Performance evidence

- Last load/specialization duration;
- recent median and tail latency;
- device and OS used for the measurement;
- thermal or throttling notes;
- link to a diagnostic trace when available.

Do not place benchmark numbers in a consumer feature screen as a promise without a measurement scope.

## Foundation Models provider design

When Core AI backs a Foundation Models session, the screen can reuse the same conversational or structured-output UI as the system model. It should still render provider-specific states:

- capability unavailable;
- model resource missing;
- tokenizer loading;
- local model preparing;
- response streaming;
- reasoning or metadata event not shown as user content;
- tool proposal awaiting app authorization;
- deterministic validation pending.

For a custom provider, a small disclosure such as “Custom on-device model” can be more honest than pretending it is the system model. If a later route uses a network provider, label that data path clearly.

## Accessibility and alternate input

The model result and its state must be usable without color, animation, or visual inspection alone.

Required design checks:

- VoiceOver announces preparation, running, partial, validation, and failure transitions once, not on every token;
- the source preview has a meaningful label and a text alternative when possible;
- a generated observation is grouped with its confidence and provenance;
- Apply, Retry, Cancel, and Use Manual Mode are real controls with stable labels;
- Dynamic Type does not clip model or error text;
- increased contrast preserves status distinction without relying on translucency;
- reduced transparency preserves hierarchy;
- reduced motion avoids a mandatory glass morph or continuous “thinking” animation;
- keyboard, Switch Control, pointer, and Full Keyboard Access can reach review and commit;
- progress is not represented only by color or a spinner;
- a custom visualization of tensors, masks, or generated media has an accessible summary.

An accessible review card should tell a person what changed and what will happen next without requiring them to inspect a generated image or animation.

## Responsive composition

On iPhone, keep source, result, and primary action in a simple vertical route. On iPad or Mac Catalyst, a split view can show source and review side by side. On visionOS or other platforms, use the same state model but redesign depth and input rather than scaling an iPhone glass card.

The layout should adapt to:

- compact and regular width;
- landscape and portrait;
- keyboard presence;
- large text;
- different source aspect ratios;
- no model or fallback mode;
- tool or approval sheets;
- multiwindow or restored task state.

Keep model work out of view body evaluation. Views render app-owned state; actors and task owners load, run, cancel, and reconcile the model.

## Design acceptance checklist

| Check | Pass condition |
| --- | --- |
| Version honesty | iOS 26 never promises the iOS 27 Core AI runtime |
| Native shell | System controls, typography, navigation, and semantics remain recognizable |
| Liquid Glass | Material supports hierarchy and touch; it does not obscure uncertainty |
| Source clarity | The person can identify the input and its revision |
| Model clarity | Route, revision, and readiness are distinguishable |
| Latency | First load, specialization, and inference states are visible and cancellable |
| Result clarity | Generated output is labeled as proposal/observation until accepted |
| Validation | Deterministic checks appear before a durable commit |
| Failure | Fallback or recovery action preserves work and explains the issue |
| Privacy | Data path and retention are understandable |
| Accessibility | State changes, results, actions, and custom visuals have semantic alternatives |
| Performance | The design remains usable under memory, thermal, and repeated-inference limits |
| Release | The visual route is tested in the signed physical-device build and TestFlight artifact |

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Core AI](https://developer.apple.com/documentation/coreai)
- [Integrating on-device AI models in your app with Core AI](https://developer.apple.com/documentation/coreai/integrating-on-device-ai-models-in-your-app-with-core-ai)
- [Compiling Core AI models ahead of time](https://developer.apple.com/documentation/coreai/compiling-core-ai-models-ahead-of-time)
- [Managing model specialization and caching](https://developer.apple.com/documentation/coreai/managing-model-specialization-and-caching)
- [Inspecting, debugging, and profiling Core AI models](https://developer.apple.com/documentation/coreai/inspecting-debugging-and-profiling-core-ai-models)
- [Running a Core AI model in a Foundation Models session](https://developer.apple.com/documentation/foundationmodels/running-a-core-ai-model-in-a-foundation-models-session)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
