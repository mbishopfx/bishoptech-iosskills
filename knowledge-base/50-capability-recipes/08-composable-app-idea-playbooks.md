# Composable App-Idea Playbooks

These playbooks are starting architectures for turning an app idea into an Apple-native build. They combine existing knowledge-base routes instead of treating “AI,” “Liquid Glass,” or a device sensor as the whole product.

Use the shared contract for every pattern:

`outcome -> input -> observation -> optional proposal -> review -> domain truth -> system surface -> proof`

The app owns authorization, validation, persistence, accessibility, and irreversible side effects. Apple frameworks provide capabilities and system surfaces; they do not remove the need to model state or verify the target device.

## Shared composition contract

| Layer | Responsibility | Default choice |
| --- | --- | --- |
| Experience shell | Navigation, states, hierarchy, accessibility, motion, and original visual identity | SwiftUI system controls and containers; system-first Liquid Glass where the OS supplies it |
| Domain truth | User-approved records, settings, permissions, and committed actions | Deterministic domain services plus SwiftData or protected files when local-first fits |
| Observation | Camera/photo/audio/location/sensor/system input | The narrow framework that owns the input: PhotosUI, VisionKit, AVFoundation, Speech, Core Location, Core Motion, ARKit, or RoomPlan |
| Intelligence | Classification, extraction, summarization, translation, or proposal generation | Deterministic code, Vision/Core ML, Speech/Translation/Natural Language, or Foundation Models only when the ambiguity justifies it |
| Review boundary | Human correction, confidence/uncertainty, validation, redaction, and approval | SwiftUI review form or focused confirmation surface |
| System surface | Search, shortcuts, widgets, Live Activities, notifications, export, Wallet, or sharing | App Intents/AppEntity, Core Spotlight, WidgetKit/ActivityKit, UserNotifications, FileDocument/Transferable, or ShareLink |
| Evidence | What was actually proven | Source -> compile/test -> simulator -> physical device -> signed/release, per claim |

## Playbook 1: Private local-first intelligence utility

### Best fit

An account-free utility where a person creates, edits, searches, and exports personal records, with AI helping organize or draft content without becoming the source of truth.

### Route

`SwiftUI + Observation -> SwiftData/protected files -> optional Foundation Models guided proposal -> review -> Core Spotlight/AppEntity -> App Intent/ShareLink`

### Responsibilities

- SwiftUI owns navigation and visible states; use native controls and semantic styles before custom effects.
- SwiftData owns small structured records; keep large media or documents in files with explicit retention and export behavior.
- Foundation Models receives only the bounded context needed for the current task and returns a proposal or typed draft.
- The person edits or approves the proposal before it becomes domain truth.
- Spotlight and App Intents expose only privacy-reviewed fields and validated actions.

### State contract

`empty -> editing -> saving -> saved -> proposal-ready -> reviewing -> accepted/rejected -> exported/indexed`

Also model unavailable AI, storage failure, stale search entry, deleted record, and export cancellation.

### Build order and proof

1. Build deterministic create/edit/delete and relaunch behavior.
2. Add local search and file export.
3. Add the AI proposal behind an availability gate and keep manual editing fully useful.
4. Add AppEntity, Spotlight, or an App Intent only for an observed user need.
5. Test local data, deletion, redaction, AI-unavailable, large attachments, accessibility, and system invocation. Physical-device proof is required for the final privacy/accessibility/system-surface claim.

Related routes: [private local-first utility](01-private-local-first-utility.md), [Foundation Models recipes](../70-code-recipes/01-foundation-model-recipes.md), [on-device AI feature skill](../skills/packages/on-device-ai-feature/SKILL.md), and [system-service recipes](../70-code-recipes/05-system-service-recipes.md).

## Playbook 2: Capture-to-reviewable record

### Best fit

Receipts, documents, labels, photos, forms, voice memos, or camera captures that become a structured record after the person reviews the extracted fields.

### Route

`PhotosPicker/VisionKit/AVFoundation -> Vision/Core ML/Speech -> typed proposal -> SwiftUI review -> SwiftData/files -> export/App Intent`

### Responsibilities

- Let the person choose or capture the source through a system picker or camera flow and explain permission at the moment of need.
- Preserve the original source separately from observations and generated text.
- Use Vision/Core ML/Speech for the measurable observation; use Foundation Models only to organize ambiguous text into a guided, validated draft.
- Show confidence, missing fields, source references, and editable values before committing.
- Keep the pipeline cancellable and resilient to blurry input, interruption, unsupported hardware, unavailable language assets, and storage failure.

### State contract

`source-selection -> permission -> capturing/importing -> analyzing -> draft -> review -> accepted/rejected -> persisted/exported`

Never route raw OCR/transcript/model text directly into a payment, reminder, health record, or other consequential action.

### Build order and proof

1. Build with fixture images/audio and a manual review form.
2. Add the selected VisionKit/PhotosUI/AVFoundation input route.
3. Add the narrow analysis framework and typed validation.
4. Add optional Foundation Models refinement after deterministic observations are stable.
5. Test simulator fixtures for layout and parsing, then physical capture, permission recovery, orientation, interruption, latency, thermal behavior, and privacy retention on representative hardware.

Related routes: [media to reviewable record](02-media-to-reviewable-record.md), [Vision/Core ML pipelines](../31-on-device-ai-recipes/03-vision-and-core-ml-pipelines.md), and [framework availability/device proof](../40-framework-routes/08-framework-availability-and-device-matrix.md).

## Playbook 3: Voice-to-structured-action

### Best fit

An app where spoken input becomes a draft task, note, reminder, search, or other bounded action that the person can inspect and confirm.

### Route

`AVFoundation audio -> Speech transcript -> Foundation Models guided output -> SwiftUI review/confirmation -> domain service/App Intent -> notification or local record`

### Responsibilities

- Keep audio capture, transcript, generated proposal, and committed action as separate values.
- Verify the exact Speech API’s authorization and processing/privacy behavior; do not label the entire Speech framework “on device.”
- Constrain the language model to a small typed schema and reject ambiguous dates, people, amounts, identifiers, or destinations.
- Require confirmation before mutating data, scheduling something, sending content, or invoking a tool with meaningful consequences.
- Offer keyboard/manual entry and a transcript-edit fallback.

### State contract

`idle -> requesting microphone/speech -> recording -> transcribing -> proposal -> reviewing -> confirmed/exited -> committed`

Include denied permission, partial transcript, audio interruption, cancellation, unavailable locale, model unavailable, invalid proposal, duplicate action, and retry.

### Build order and proof

1. Build a typed manual-input flow with deterministic validation.
2. Add recorded-audio fixtures and transcript editing.
3. Add live capture/transcription with an explicit permission gate.
4. Add guided generation only for normalization or proposal extraction.
5. Test microphone, interruptions, locale, network/privacy behavior of the chosen Speech API, model availability, confirmation, and physical-device audio routing.

Related routes: [speech, translation, and language](../31-on-device-ai-recipes/04-speech-translation-and-language-routes.md), [Foundation Models typed output](../31-on-device-ai-recipes/01-guided-generation-and-typed-output.md), and [system-surface-first feature](05-system-surface-first.md).

## Playbook 4: Private on-device personal assistant

### Best fit

An assistant for a person’s own local records that can answer bounded questions, propose changes, or expose a small number of validated actions through the app and Apple system surfaces.

### Route

`SwiftData/local files -> privacy-reviewed Core Spotlight/AppEntity index -> Foundation Models read-only tools -> answer or typed proposal -> review/confirmation -> App Intent/Widget/Shortcut`

### Responsibilities

- Keep context selection deterministic and minimal; do not dump a whole database, raw media, identity data, or private notes into a prompt by default.
- Use read-only tools to retrieve current local facts; the model is a planner/explainer, not the database or permission authority.
- Return citations/source records or a clear “not found/uncertain” state when the person needs to trust the answer.
- Turn mutations into a separate typed proposal and confirmation route.
- Expose only the few App Intents that shorten a real workflow and preserve a useful in-app/manual path.

### State contract

`checking availability -> selecting bounded context -> answering -> source review -> proposed action -> confirmation -> committed or discarded`

Also model context overflow, stale index, unavailable model, tool failure, sensitive-content refusal, cancellation, and empty local data.

### Build order and proof

1. Build deterministic local search and typed domain actions.
2. Add a read-only tool with bounded queries and source identifiers.
3. Add Foundation Models output with prompt/schema versioning and evaluation fixtures.
4. Add a review surface and only then expose selected App Intents, Spotlight entities, widgets, or shortcuts.
5. Test privacy minimization, stale/deleted records, malicious prompt content, unavailable model, tool failure, confirmation, and physical Apple Intelligence configurations.

Related routes: [tools, agents, and side effects](../30-on-device-ai/03-tools-agents-and-side-effects.md), [Core Spotlight/App Entities](../44-system-services/00-privacy-and-device-services.md), and [on-device AI feature skill](../skills/packages/on-device-ai-feature/SKILL.md).

## Playbook 5: Live device session

### Best fit

An audio player, workout, timer, navigation flow, recorder, live analyzer, or sensor experience where state changes while the person remains in the flow.

### Route

`SwiftUI shell -> AVFoundation/Core Location/Core Motion/Vision/Speech -> cancellable session service/actor -> checkpoints -> ActivityKit/WidgetKit/UserNotifications`

### Responsibilities

- Define a session lifecycle independent from the view: idle, preparing, active, paused, interrupted, finishing, complete, failed, and cancelled.
- Keep capture/measurement state separate from presentation state and persist checkpoints when losing the process would harm the user outcome.
- Request permission immediately before the live feature and stop capture when the feature no longer needs it.
- Use ActivityKit only for useful glanceable status; it is not the canonical session store.
- Make background, phone-lock, audio-route, network, thermal, battery, and interruption behavior explicit rather than assumed.

### Proof

Use simulator/fake data for state-machine tests, then physical devices for capture, sensor accuracy, audio routing, battery, thermal behavior, lock screen, interruptions, and Live Activity delivery. Do not claim background continuity from a foreground demo.

Related routes: [live session](03-live-session.md), [media and sensor recipes](../70-code-recipes/03-media-and-sensor-recipes.md), and [ActivityKit](https://developer.apple.com/documentation/activitykit/).

## Playbook 6: Spatial field notebook

### Best fit

Room scans, spatial measurements, AR annotations, 3D inspection, or a field record that needs real-world context and an exportable result.

### Route

`SwiftUI shell -> ARKit/RealityKit/RoomPlan session -> anchors/measurements/observations -> review -> SwiftData/files -> ShareLink/FileDocument/export`

### Responsibilities

- Define the real-world outcome first: measure, place, inspect, scan, or play.
- Keep world anchors/measurements and confidence/source context separate from visual-only RealityKit entities.
- Request camera/world-sensing permission at the start of the spatial flow and provide a non-spatial fallback where the outcome allows it.
- Treat measurements and model observations as estimates that need review when a person may rely on them.
- Preserve the session/export context so another person can understand how a result was produced.

### Proof

Use simulator fixtures for non-sensor UI and serialization, then supported physical hardware for tracking, LiDAR/camera behavior, lighting, relocalization, interruptions, performance, thermal limits, and export accuracy. A rendered scene is not proof that a measurement matches the physical world.

Related routes: [spatial experience](07-spatial-experience.md), [RealityKit/ARKit deep dive](../42-framework-deep-dives/04-realitykit-arkit-and-spatial.md), and [RoomPlan](https://developer.apple.com/documentation/roomplan).

## Composition rules

| If the idea needs… | Add… | Keep separate… |
| --- | --- | --- |
| A polished Apple-native surface | SwiftUI + system components + restrained Liquid Glass | Product identity and proprietary Apple branding |
| Structured extraction | Vision/Speech/Translation or Core ML first; Foundation Models guided output second | Observations, generated proposal, approved record |
| Natural-language action | App Intent/tool with validation and confirmation | Model planning and irreversible side effect |
| Local privacy | SwiftData/files + bounded context + local indexing | Sensitive data and unnecessary remote services |
| Live status | ActivityKit/WidgetKit/notifications | System surface and canonical session state |
| Physical-world understanding | Vision/ARKit/RoomPlan/Core Motion | Visual effects and evidence about physical truth |

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [VisionKit](https://developer.apple.com/documentation/visionkit/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Core ML](https://developer.apple.com/documentation/coreml/)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications)
- [ShareLink](https://developer.apple.com/documentation/swiftui/sharelink)
- [FileDocument](https://developer.apple.com/documentation/swiftui/filedocument)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [RealityKit](https://developer.apple.com/documentation/realitykit)
- [RoomPlan](https://developer.apple.com/documentation/roomplan)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [Core Motion](https://developer.apple.com/documentation/coremotion)
