# Advanced Foundation Models provider and multimodal design for SwiftUI

An advanced intelligence screen should make provider choice, source material, workflow phase, and user control legible without turning the interface into a technical dashboard. The person needs to know what the feature is doing, what data it is using, what may happen next, and how to stop or recover.

The native design goal is not to imitate an Apple Intelligence system screen. It is to use SwiftUI conventions, Liquid Glass hierarchy, accessible controls, and clear source/provenance language while letting the product own its workflow.

## The design contract

Every advanced route answers four visible questions:

1. What task is being performed?
2. Which source or attachment is in context?
3. Is the work on device, private cloud, or another configured provider?
4. Is the result a draft, an observation, a tool proposal, or a committed action?

Do not hide these answers behind a sparkle icon, a shimmer, or a generic “thinking” label.

## Provider selector

Provider choice is a product and privacy decision. It should not be a free-form toggle exposed before the user understands the tradeoff.

| Provider state | Visible copy | Available action |
| --- | --- | --- |
| on-device ready | On-device suggestion | generate |
| on-device unavailable | On-device model unavailable | use fallback or retry |
| PCC available | Private cloud suggestion with quota status | choose if policy allows |
| PCC quota near limit | Private cloud usage is nearly at its daily limit | use on-device or wait |
| PCC quota reached | Private cloud limit reached | use on-device or standard workflow |
| custom local model ready | Local model | generate |
| external provider configured | External service | review data policy and generate |
| provider capability missing | This model cannot analyze images or use tools | choose another route |

If the user does not need to choose, use app policy and state the route in a secondary status label. If the user does need to choose because data leaves the device, make that choice deliberate and persistent.

## Source and attachment surface

### Image intake

Use a standard PhotosPicker, camera route, file importer, or existing media selection flow. The attachment review should show:

- thumbnail or preview;
- source type;
- orientation or crop when relevant;
- source identity or revision;
- remove or replace;
- whether the image is being sent to a private cloud or external provider;
- what the model is being asked to inspect.

Do not present a model description as if it were a camera measurement. Keep original metadata and derived model output conceptually separate.

### Multi-attachment layout

For two or more images, use a compact horizontal strip or a two-column grid with explicit labels. Avoid ambiguous order. If the prompt compares first and second images, the UI should preserve that ordering.

| Attachment UI | Meaning |
| --- | --- |
| numbered source chip | stable order in a comparison |
| label chip | model/tool reference such as document-page |
| selected outline | currently included in the prompt |
| warning badge | source missing, orientation uncertain, or unsupported |
| privacy note | provider data-flow change |

If the image is a video frame or CVPixelBuffer, show the source context accurately. A captured frame is not the same as the entire video.

## Dynamic profile as a screen state

Dynamic profiles change model configuration, instructions, tools, and history view as the app moves through a workflow. The UI should reflect the active phase without exposing every internal modifier.

| Phase | Screen emphasis | Tool surface |
| --- | --- | --- |
| inspect | source and question | read-only image/OCR tools |
| understand | structured observations | Vision or Core ML tools |
| plan | proposed steps | read-only app search |
| enrich | more context | provider-specific read tools |
| review | typed candidate | no hidden side effects |
| approve | consequence and scope | explicit write action |
| commit | deterministic progress | app-owned operation |

When a profile transition changes the provider or data path, use a status message rather than a decorative animation alone. Preserve input, cancellation, and fallback controls across the transition.

## Liquid Glass composition

Use Liquid Glass for functional groupings:

- provider/status control cluster;
- attachment actions;
- profile phase controls;
- review and approval actions.

Use a GlassEffectContainer or the current native container pattern when multiple controls belong together. Keep the content source and generated result on ordinary readable surfaces unless a glass treatment materially helps hierarchy.

Glass rules:

1. standard controls first;
2. material second;
3. motion third;
4. no glass-only meaning;
5. no animation that implies certainty;
6. no hidden stop or deny action;
7. preserve contrast and large text;
8. provide reduced-motion and fallback behavior.

An on-device label, private-cloud label, or external-service label should remain readable when materials are reduced or unavailable.

## Multimodal review card

A useful review card has five layers:

1. source: what the model saw;
2. task: what it was asked to do;
3. observation: what it produced;
4. confidence or limitation: what is uncertain or unsupported;
5. next action: edit, retry, compare, save, or dismiss.

For OCR and barcode results, show the specialized tool or source where it matters. For a generated caption or alt-text draft, let the person edit it before saving. For classification, show the finite label set and the ability to correct it.

Avoid words such as detected, verified, identified, or measured unless the underlying route can justify them. A model interpretation should normally be called a suggestion, draft, or observation.

## Agentic workflow surface

An agentic route needs a visible call graph without overwhelming the main task. Use a disclosure row or history sheet:

- current phase;
- tools used;
- data sources consulted;
- pending action;
- elapsed time;
- cancel;
- retry;
- privacy boundary.

Do not show internal reasoning as if it were a fact record. When the framework supplies reasoning or metadata, follow the product and privacy policy and prefer concise action summaries. A tool call should be represented as a capability use, not as a command the user already approved.

### Approval sheet

An approval sheet should:

- name the action;
- show affected records or recipients;
- show data that will be sent;
- show the source revision;
- state whether the action is reversible;
- use a consequence-specific confirm button;
- offer deny and edit;
- recheck state when confirming.

If a profile can route to a write tool, the UI must make the transition from suggestion to authorized action explicit.

## Context and history design

Long context should not become a long scroll of hidden model history. Offer:

- current source;
- recent user decisions;
- compact summaries;
- tool result provenance;
- remove from context;
- start a new task.

When historyTransform narrows the context for a provider, the UI can show a small “Using selected context” state. Do not promise that the model remembers an entry if the current profile excludes it.

For a provider handoff, state what carries forward:

| Handoff | User-facing explanation |
| --- | --- |
| on-device to PCC | More context may be used through Private Cloud Compute |
| PCC to on-device | Continuing with a smaller local context |
| image to text | Using extracted text from the selected image |
| plan to review | The app created a draft proposal for your review |

## Accessibility

The screen must be understandable without visual material:

- announce provider and phase changes;
- label attachments by order and purpose;
- expose source removal and privacy controls;
- describe partial output as partial;
- make cancel, retry, deny, and confirm actions reachable;
- do not use a sparkle icon as the only label;
- use accessibilityValue for provider status and quota state;
- keep focus stable when profile controls morph;
- move focus to a new approval sheet and return it after dismissal;
- support Dynamic Type without clipping image labels or tool status;
- support Reduce Motion without removing state transitions;
- support keyboard, pointer, Switch Control, and Full Keyboard Access.

If the image itself is inaccessible, the model-generated description is still a draft until the user accepts it or a deterministic accessibility policy owns it.

## Privacy copy

Use precise microcopy:

- “This image stays on device for this suggestion.”
- “This step uses Private Cloud Compute and may count toward a daily limit.”
- “The selected image and prompt are sent to the configured provider.”
- “The app uses OCR to read text from this image before drafting a summary.”
- “Review the suggestion before saving.”
- “No changes were made.”

Do not claim “private” without knowing the provider’s data path. Do not display raw prompt or tool data in notifications, previews, logs, or screenshots.

## Responsive layouts

### iPhone

- one source or attachment region;
- bottom sheet for provider and approval;
- compact tool/history disclosure;
- thumb-reachable cancel;
- result card below source.

### iPad

- split source and review panes;
- provider and context inspector;
- keyboard-first commands;
- multiple attachments with labels;
- approval in a focused sheet or inspector.

### Mac Catalyst or macOS

- menu command and keyboard shortcut;
- resizable source and result columns;
- provider/context inspector;
- explicit external-service settings;
- standard toolbar and command validation.

### Widget and system surfaces

Do not embed a mutable multimodal agent in a widget. Expose a narrow App Intent or a deterministic snapshot, then open the full app for source selection, provider disclosure, and approval.

### watchOS, CarPlay, and other constrained surfaces

Use only the approved platform route. A long image analysis or provider handoff should not be disguised as a short glance. Move the work to the paired app or a supported system surface.

## Design tokens for uncertainty

Use semantic roles rather than “AI colors”:

| Role | Semantic use |
| --- | --- |
| secondary label | provider, source, or draft status |
| accent | current actionable control |
| warning | quota, missing source, or needs review |
| destructive | delete or irreversible action |
| success | deterministic commit completed |
| material | grouping and hierarchy, not truth |

The same design should survive color-blindness, high contrast, reduced transparency, and no animation.

## Design acceptance checklist

- provider and data path are understandable;
- source attachments are ordered, labeled, removable, and privacy-reviewed;
- profile phase is visible when it changes what the model can do;
- history scope is honest;
- tool graph is inspectable enough for the task;
- write actions have a consequence-specific approval;
- model output is visibly provisional until validated;
- Liquid Glass groups controls without hiding the source;
- PCC quota and unavailable states are designed;
- custom provider capabilities are checked before offering the route;
- image orientation and source provenance survive into review;
- VoiceOver and alternate input can complete every action;
- iPhone and iPad layouts keep cancel and deny reachable;
- fallback paths work without a model;
- tests cover provider handoff and profile transitions;
- physical-device and release evidence are planned.

## Related local routes

- [Advanced provider and multimodal deep dive](../42-framework-deep-dives/112-swiftui-foundation-models-advanced-provider-multimodal-route-review.md)
- [Advanced provider and multimodal capability route](../50-capability-recipes/143-swiftui-foundation-models-advanced-provider-multimodal-route-review-route.md)
- [Foundation Models production design](../21-design-deep-dives/139-swiftui-foundation-models-production-route-review-design.md)
- [AI review shell and glass state](../20-liquid-glass/06-ai-review-shell-and-glass-state.md)
- [PhotosPicker and media-source review](../42-framework-deep-dives/102-swiftui-photospicker-photokit-imageio-live-photo-source-review.md)
- [Vision and Core ML live-observation review](../42-framework-deep-dives/95-swiftui-vision-core-ml-live-observation-review.md)
- [Accessibility and adaptability checklist](../60-verification/02-accessibility-and-adaptability-checklist.md)
- [Privacy, performance, and release proof](103-release-ready-native-design-and-privacy.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [PrivateCloudComputeLanguageModel](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel)
- [Composing dynamic sessions with instructions and profiles](https://developer.apple.com/documentation/foundationmodels/composing-dynamic-sessions-with-instructions-and-profiles)
- [DynamicInstructions](https://developer.apple.com/documentation/foundationmodels/dynamicinstructions)
- [LanguageModelSession.Profile](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/profile)
- [Attachment](https://developer.apple.com/documentation/foundationmodels/attachment)
- [ImageReference](https://developer.apple.com/documentation/foundationmodels/imagereference)
- [Analyzing images with multimodal prompting](https://developer.apple.com/documentation/foundationmodels/analyzing-images-with-multimodal-prompting)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Evaluations](https://developer.apple.com/documentation/evaluations)
- [Analyzing the runtime performance of your Foundation Models app](https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
