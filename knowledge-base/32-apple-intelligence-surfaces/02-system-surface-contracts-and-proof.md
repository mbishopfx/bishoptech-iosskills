# Apple Intelligence System Surface Contracts and Proof

## System-owned intelligence is a different route

Some Apple Intelligence experiences are owned by the system. The app contributes text views, semantic content, App Intents, entities, actions, images, or supported configuration; it does not own the system’s model prompt, ranking, presentation, or availability decision.

Keep the boundary visible:

| Surface | App contributes | System owns | App proof must cover |
| --- | --- | --- | --- |
| Writing Tools | Standard text editing surface or documented custom text-engine integration. | Writing, proofreading, rewriting, and system presentation. | Text semantics, editing behavior, privacy, availability, and the actual text surface. |
| Visual Intelligence | App Intents, searchable entities, semantic content, and matching/deep-link behavior. | Context capture, search/presentation, ranking, and user invocation. | Entity relevance, privacy scope, result resolution, destination, and supported device/system surface. |
| Siri/Apple Intelligence actions | App Intents, parameters, entities, dialogs, and domain use cases. | Natural-language interpretation, invocation context, and system response. | Intent resolution, authorization, side effects, error dialog, and supported invocation route. |
| Spotlight | App entities, indexing/donation, display representations, and destination. | Indexing/search presentation and ranking. | Stable identifiers, stale/deleted records, privacy, result relevance, and deep link. |
| Image Playground | Documented image-generation integration or system UI entry point. | Generation model, safety behavior, presentation, and availability. | Input/output handoff, user control, persistence, attribution/disclosure, and fallback. |
| Widgets, controls, Live Activities | App Intents, timeline/state data, configuration, and bounded action. | Surface lifecycle, refresh/presentation, and system execution context. | Extension/process boundary, stale state, authorization, action result, and deep link. |

Do not call these routes “your on-device model” unless the app is actually using the documented API that makes that claim. A system-owned surface can be private or on-device in a particular configuration while still requiring separate app integration and runtime proof.

## Contract before styling

For every system surface, define:

1. **Entry:** how the person or system invokes it, and whether the app UI is running.
2. **Input:** the app content/entity/action that is exposed, including privacy and redaction rules.
3. **Resolution:** how identifiers, parameters, locale, and current state are resolved.
4. **Ownership:** which UI, model behavior, ranking, and availability decisions belong to Apple versus the app.
5. **Action:** what deterministic use case can run, what authorization it needs, and whether confirmation is required.
6. **Return:** the result, dialog, deep link, stale/error state, or manual route.
7. **Evidence:** the actual system surface and configuration used to verify the claim.

## Keep the app useful without the surface

System-surface availability can depend on OS, device, region, language, settings, account state, entitlements, and the system’s own readiness. The core app should still work if:

- Apple Intelligence is disabled or unavailable;
- the person has not enabled a system feature;
- an App Intent cannot resolve an entity;
- a widget/control has stale or unavailable shared data;
- a language or image asset is not installed;
- a system-owned sheet or presentation cannot be shown;
- the user rejects the action or the app process is not available.

Fallbacks should preserve the underlying outcome: open the app at a review screen, use manual search, show the original text/image, offer a deterministic action, or save a draft for later.

## Original product identity

Use Apple’s semantic conventions and system components without copying Apple-owned screens, names, icon lockups, marketing language, or proprietary visual identity. A custom product can feel native through:

- clear task hierarchy;
- standard App Intent and SwiftUI semantics;
- system typography and accessibility behavior;
- content-first layout;
- restrained functional Liquid Glass where the system route does not already provide the treatment;
- honest loading, unavailable, review, and failure states.

Do not make the system surface look like a fake Apple app. Make the app’s own outcome obvious when the person returns from a system-owned interaction.

## Proof matrix

| Claim | Minimum evidence |
| --- | --- |
| “The app has an App Intent.” | Target compile and intent metadata inspection. |
| “The action resolves in Shortcuts/Siri/Apple Intelligence.” | Actual invocation, parameter/entity resolution, authorization, and result on the named supported configuration. |
| “Content appears in Spotlight or Visual Intelligence.” | Indexed/donated content, actual system search/context, result relevance, privacy behavior, and deep link. |
| “Writing Tools works in the editor.” | Supported text surface, system UI invocation, editing result, undo/correction, and accessibility behavior. |
| “The widget/control/Live Activity performs the action.” | Extension/system-surface run, shared-state read/write, stale/error handling, and physical device where required. |
| “Image Playground integration is available.” | Target SDK/availability, actual system view or documented integration path, user approval, persistence, and fallback. |
| “The experience is private/on device.” | Exact API/data path, runtime configuration, disclosure, logging/retention review, and no unsupported inference from the UI. |

A preview or in-app button only proves that the app can render its own fallback or entry point. It does not prove system discovery, ranking, Apple Intelligence model availability, or production delivery.

## Sources

- [Apple Intelligence](https://developer.apple.com/documentation/technologyoverviews/apple-intelligence/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Making app entities available in Spotlight](https://developer.apple.com/documentation/appintents/making-app-entities-available-in-spotlight)
- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [Widgets, Live Activities, and controls](https://developer.apple.com/documentation/appintents/widgets-live-activities-and-controls)
- [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
