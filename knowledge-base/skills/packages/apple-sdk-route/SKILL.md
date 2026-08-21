---
name: apple-sdk-route
description: Turn an iOS app idea into an Apple-native framework route, state/data boundary, system-surface plan, permission matrix, and proportional verification plan.
metadata:
  short-description: Route iOS ideas through Apple SDKs
---

# Apple SDK Route

Use this skill at the start of a new iOS app or feature, or when an existing implementation has accumulated framework, permission, data, or system-surface confusion. It produces an architecture route and evidence plan; it does not authorize a backend, account system, deployment, or production integration by itself.

## Read before acting

Inspect the workspace and the idea:

- locate the actual app target, deployment target, platform/device family, modules, persistence, networking, entitlements, Info.plist keys, and existing system integrations;
- write the outcome in one sentence, then list source/input, transformation, destination, user-controlled side effects, offline requirement, privacy sensitivity, system surfaces, commerce needs, and supported platforms;
- read the [framework catalog](../../../40-framework-routes/00-framework-catalog.md), [framework selection questionnaire](../../../00-foundations/06-framework-selection-questionnaire.md), [idea-to-route recipe](../../../50-capability-recipes/00-idea-to-route.md), and the relevant framework deep dive from the [knowledge-base map](../../../README.md);
- refresh the exact official framework pages in the [source registry](../../../sources/official-source-registry.md) before relying on an API name, availability claim, permission key, entitlement, or system behavior.

## Routing method

1. Start from the user outcome and the smallest trusted transformation, not from a favorite framework.
2. Select the narrowest Apple route that owns the capability: SwiftUI/UIKit for presentation, SwiftData for local model state, CloudKit for Apple-platform sync, StoreKit for commerce, App Intents for system discoverability, AVFoundation/PhotosUI/VisionKit for media, MapKit/Core Location for location, HealthKit/HomeKit/Bluetooth for protected device data, Network/URLSession for transport, and the relevant system extension or surface when the feature must live outside the app process.
3. Draw the handoff: input -> framework observation/operation -> validation -> domain truth -> derived presentation -> system surface. Keep UI state, persistence, generated/model output, and external system state distinct.
4. List every permission, entitlement, Info.plist usage description, account/developer capability, background mode, device requirement, language/region condition, and OS availability that the route may need. Mark each as “to verify,” never as implied by the framework name.
5. Design unavailable, denied, offline, empty, stale, interrupted, rate-limited, and partial-success paths before the happy path. Preserve a manual or local-first route when it can satisfy the underlying goal.
6. Choose evidence proportional to risk: source review, unit/preview tests, simulator, physical device, permission reset, system-surface invocation, signed build, App Store/TestFlight, or production verification. Name what each proves and what it cannot prove.
7. Record the route and source links in the project’s planning artifacts or the [knowledge-base templates](../../../90-templates/design-brief.md) before implementation grows beyond a small slice.

## Change boundary

May inspect project structure and add or update scoped planning, route, state, permission, entitlement, and verification documentation. During implementation, may change the selected feature’s modules and directly related configuration only when the user asked to build it. Do not infer authorization for new accounts, cloud storage, analytics, paid services, background execution, health data, production credentials, deployment, or contacting users.

## Refuse to assume

- every app needs a backend, account, or CloudKit;
- CloudKit is automatically the correct sync strategy;
- a framework’s existence or a symbol’s name proves target-SDK availability;
- a permission prompt at launch is good UX or sufficient authorization design;
- simulator output proves camera, sensors, GPU, Watch, CarPlay, Apple Intelligence, App Clip, entitlement, or App Store behavior;
- local-first data can be moved to a server without changing the privacy contract;
- a system surface is “done” because the app’s main screen works.

## Route deliverable

Produce:

- selected framework route and rejected alternatives;
- module and data boundaries;
- state machine and user-facing fallback plan;
- permission/entitlement/Info.plist/account/device matrix;
- implementation order with the smallest testable slice first;
- source registry links and verification gates;
- explicit proof gaps, especially physical-device, system-surface, privacy, commerce, and release gaps.

Keep the route concise enough to use as a build plan, but specific enough that another agent can inspect the same target and reach the same next verification step.

## Related knowledge-base routes

- [Framework catalog](../../../40-framework-routes/00-framework-catalog.md)
- [Capability recipes](../../../50-capability-recipes/00-idea-to-route.md)
- [Framework deep dives](../../../41-framework-deep-dives/README.md)
- [System framework deep dives](../../../43-system-framework-deep-dives/README.md)
- [Permission, entitlement, and privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [System-surface checklist](../../../60-verification/05-system-surface-checklist.md)

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
