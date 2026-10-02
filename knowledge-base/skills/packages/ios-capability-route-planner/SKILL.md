---
name: ios-capability-route-planner
description: Turn an iOS app idea or feature request into an Apple-native capability route, framework/symbol choices, SwiftUI and Liquid Glass surface plan, on-device AI boundaries, permission/entitlement/privacy matrix, lifecycle/fallback contract, and proportional verification plan. Use when planning, reviewing, or debugging a native iOS/iPadOS/watchOS/CarPlay/App Clip/spatial feature before implementation or when a project has framework, system-surface, device, or evidence confusion.
---

# iOS Capability Route Planner

Turn an idea into a capability route and evidence plan before framework choices harden into implementation. Preserve native Apple behavior, original product identity, privacy boundaries, and honest device/system/release claims.

`outcome -> narrow Apple route -> state/data boundary -> native surface -> permission/entitlement -> lifecycle/fallback -> verification evidence`

## Read before acting

- Inspect the actual repository and target: Xcode project/workspace, schemes, deployment target, platforms/device families, modules, persistence, networking, extensions, entitlements, `Info.plist`, privacy manifest, assets, existing system surfaces, and current tests.
- Read the [knowledge-base map](../../../README.md), [capability-first Apple SDK atlas](../../../40-framework-routes/10-capability-first-apple-sdk-atlas.md), [framework availability and device-proof matrix](../../../40-framework-routes/08-framework-availability-and-device-matrix.md), and the relevant [deep-dive indexes](../../../41-framework-deep-dives/README.md), [device/system routes](../../../42-framework-deep-dives/README.md), and [system framework routes](../../../43-system-framework-deep-dives/README.md).
- For design work, read the [native screen composition atlas](../../../21-design-deep-dives/08-native-screen-composition-atlas.md), [functional Liquid Glass interactions](../../../20-liquid-glass/05-functional-glass-interactions.md), [accessibility/adaptation recipes](../../../70-code-recipes/12-accessibility-adaptive-and-native-design-recipes.md), and the [iOS 27 native design brief](../../../90-templates/ios27-native-design-brief.md).
- For iOS 27 SwiftUI, performance, or on-device claims, read the [iOS 27 SwiftUI and SDK refresh](../../../10-swiftui/13-ios27-swiftui-refresh.md) and [performance/on-device proof template](../../../90-templates/ios27-performance-and-on-device-proof.md).
- For intelligence work, read the [AI feature lifecycle](../../../30-on-device-ai/09-ai-feature-lifecycle-and-availability.md), [AI evaluation discipline](../../../30-on-device-ai/10-on-device-ai-evaluation-and-model-update-discipline.md), and [reviewable multimodal pipeline](../../../31-on-device-ai-recipes/06-reviewable-multimodal-ai-pipeline.md).
- Refresh the exact official Apple/Swift pages in the [source registry](../../../sources/official-source-registry.md) before relying on a symbol, availability condition, entitlement, system surface, or iOS 26/27 behavior.

## Route workflow

1. State the outcome in one sentence. Record the entry point, primary action, accepted result, consequence of error, offline requirement, privacy sensitivity, and supported platforms.
2. Classify the capability: present/edit, persist/sync, capture/analyze, communicate, locate/map/weather, use protected data, control a device, transact/authenticate, expose to the system, share/export, run in the background, build spatial/graphics/game content, or extend to a companion surface.
3. Select the narrowest Apple route. Prefer SwiftUI/UIKit/system-owned surfaces, PhotosUI/file import, Vision/Core ML, Speech/Translation, MapKit/Core Location, HealthKit/Contacts/EventKit, StoreKit/PassKit/AuthenticationServices, App Intents/WidgetKit/ActivityKit, and the relevant device/companion framework before inventing a custom service.
4. Name concrete symbols and rejected alternatives. Record why the route owns the capability, what it does not own, and which API signatures/availability annotations still require the selected Xcode/SDK check. Keep beta-only adaptive arrangement and reserved-region APIs separate from stable routes.
5. Draw the handoff: `input -> framework observation/operation -> normalized app evidence -> deterministic validation -> domain truth -> derived presentation -> system/companion handoff`.
6. Build the state matrix before the happy path. Include checking, ready, denied, restricted, unsupported, unavailable, not-ready, loading, partial, stale, interrupted, cancelled, expired, empty, invalid, conflict, and completed states where relevant.
7. List every permission, usage description, entitlement, background mode, App Group, associated domain, merchant/account/service setup, language/asset condition, hardware requirement, and server dependency. Mark unknowns `to-verify` rather than inferring them from a framework name.
8. Design the native surface. Use semantic controls, system typography, adaptive containers, correct navigation/tab/toolbar/sheet ownership, Dynamic Type, VoiceOver, reduced motion/transparency, localization, keyboard/pointer/controller input, and a manual fallback. Use Liquid Glass system adoption first; add custom glass only to a functional related group that needs it.
9. Choose proportional evidence. Separate source, compile, preview/fixture, simulator, physical device, two-device/accessory/vehicle, system surface, signed artifact, TestFlight/App Store, server/account, and production proof.
10. Produce the route plan and stop before implementing unless the user explicitly asked for the build. If implementation is requested, keep the first slice narrow and make the route’s verification gates executable in the target project.

## Fast path

For one feature, compare no more than the plausible capability lanes against outcome ownership, target availability, setup cost, fallback, and required proof. Pick the first route that satisfies the outcome with the least irreversible configuration, then record the other lanes as rejected or deferred. Expand the matrix only when a new requirement changes that decision.

## Capability decision table

| Need | Start route | Do not assume |
| --- | --- | --- |
| Native screen/navigation/design | SwiftUI, UIKit bridge where necessary, HIG, Liquid Glass system adoption | A custom replica is more native than a standard control. |
| Local records/files | SwiftData, Core Data, FileDocument, DocumentGroup, security-scoped URLs | CloudKit, an account, or a server is required. |
| Text generation/typed proposal | Foundation Models with availability, guided output, validation, review | Model availability, correctness, or domain truth. |
| Image/video observation | Vision/VisionKit/Core ML/AVFoundation | Confidence is truth or a simulator is camera proof. |
| Speech/translation/audio | SpeechAnalyzer/SpeechTranscriber, TranslationSession, Natural Language, Sound Analysis, AVAudioSession | All Speech APIs are on-device or every locale has the same assets/quality. |
| Map/location/weather | MapKit, Core Location, CoreLocationUI, WeatherKit | A map requires location permission or a forecast is current/guaranteed. |
| Health/personal data | HealthKit, Contacts, EventKit, UserNotifications | Authorization is permanent, complete, or medical validation. |
| Commerce/identity/security | StoreKit 2, PassKit, AuthenticationServices, Keychain, LocalAuthentication, CryptoKit, DeviceCheck/App Attest | Local state proves payment, identity, entitlement, or integrity. |
| System discoverability | App Intents, AppEntity, EntityQuery, Spotlight, WidgetKit, ActivityKit | An in-app action proves Siri/Spotlight/widget/control delivery. |
| Physical/accessory/companion | HomeKit, Core Bluetooth, Nearby Interaction, NFC, WatchConnectivity, CarPlay, CallKit/LiveCommunicationKit | Discovery is trust, pairing is compatibility, or one device proves a two-device route. |
| Documents/background/extensions | FileProvider, sharing, WebKit/PDFKit, App Groups, BackgroundTasks, App Clips | Background execution is scheduled on demand or an extension shares in-memory app state. |
| Spatial/graphics/games | ARKit, RealityKit, Metal, SpriteKit, GameplayKit, GameKit | Static assets, simulator, or a debug frame rate proves physical tracking/performance. |

## Architecture and proof contract

Return a compact table or document with these fields:

| Field | Required content |
| --- | --- |
| Outcome and consequence | User task, primary action, acceptable failure, and reversibility. |
| Selected route | Frameworks, concrete symbols, target platforms, rejected alternatives, and API questions. |
| Data boundary | Source, representation, normalization, persistence, sync, retention, deletion, and derived values. |
| UI/system boundary | SwiftUI/UIKit/system/extension/Watch/CarPlay/spatial surface, navigation, review, deep link, and fallback. |
| State/lifecycle | Permission, availability, start/stop/cancel/interrupt/background/process/account/asset states. |
| Trust boundary | Deterministic validation, authorization, confirmation, idempotency, conflict, and side-effect policy. |
| Configuration | Entitlements, usage descriptions, privacy manifest, background modes, App Groups, domains, accounts, and server dependencies. |
| Tests | Fixtures, unit/UI/accessibility/performance tests, simulator, physical/two-device/system tests. |
| Evidence gaps | Exact claims not yet proven and the next smallest verification action. |

## Evidence rules

- Treat Apple documentation as source evidence, not compile or runtime proof.
- Treat a preview as visual/state evidence, not accessibility, hardware, model, entitlement, or release evidence.
- Treat a simulator as UI/system-flow evidence only where the simulated route is documented; it does not prove camera, microphone, sensors, haptics, radio, GPU/thermal, Apple Intelligence, Watch, CarPlay, App Clip, protected data, or production behavior.
- Treat a physical-device run as proof only for the device/build/configuration and task actually tested.
- Treat a system-surface invocation as proof of that invocation, not all devices, all languages, all users, or production delivery.
- Treat a signed archive/TestFlight/App Store build as a separate release boundary; do not claim App Review approval or production behavior from an archive.

## Refuse to assume

- Do not add a backend, account, analytics, paid service, cloud sync, health access, background mode, or production credential without a stated product need and authorization.
- Do not copy Apple-owned screens, branding, icons, wording, or proprietary visual identity; use native conventions with original hierarchy and copy.
- Do not call a generated proposal, observation, transcript, translation, location, weather value, health sample, transaction, or system entity domain truth without the relevant deterministic validation and review policy.
- Do not make permission, entitlement, device, language, model, service, accessibility, performance, privacy, or release claims from a framework name or code snippet.

## Related routes

- [Capability-first Apple SDK atlas](../../../40-framework-routes/10-capability-first-apple-sdk-atlas.md)
- [Cross-framework feature lifecycle](../../../41-framework-deep-dives/06-cross-framework-feature-lifecycle.md)
- [System-surface and extension composition](../../../43-system-framework-deep-dives/06-system-surface-and-extension-composition.md)
- [Device and companion capability contracts](../../../42-framework-deep-dives/08-device-and-companion-capability-contracts.md)
- [Apple-native design and Liquid Glass verification](../ios-native-design-verification/SKILL.md)
- [On-device intelligence evaluation](../ios-on-device-intelligence-evaluation/SKILL.md)
- [System surfaces and background](../ios-system-surfaces-and-background/SKILL.md)
- [Companion and communications](../ios-companion-communications/SKILL.md)
- [Device and release proof](../ios-device-release-proof/SKILL.md)
- [iOS 27 SwiftUI and SDK refresh](../../../10-swiftui/13-ios27-swiftui-refresh.md)
- [iOS 27 native design brief](../../../90-templates/ios27-native-design-brief.md)
- [iOS 27 performance and on-device proof](../../../90-templates/ios27-performance-and-on-device-proof.md)

## Sources

- [Current iOS 27/Xcode 27 source registry](../../../sources/official-source-registry.md)
- [Xcode SDK and system requirements](https://developer.apple.com/xcode/system-requirements)
- [SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui)
- [ArrangementView styles](https://developer.apple.com/documentation/swiftui/view/arrangementviewstyle%28_%3A%29)
- [SwiftUI GeometryProxy and reserved regions](https://developer.apple.com/documentation/swiftui/geometryproxy)
- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Designing for iOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ios)
- [Designing for iPadOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-ipados)
- [Designing for macOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-macos)
- [Designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)
- [Designing for games](https://developer.apple.com/design/human-interface-guidelines/designing-for-games)
- [Designing for iPhone Duo](https://developer.apple.com/design/human-interface-guidelines/designing-for-iphone-duo)
- [Apple Design Resources](https://developer.apple.com/design/resources/)
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [Speech](https://developer.apple.com/documentation/speech/)
- [Translation](https://developer.apple.com/documentation/translation)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [HealthKit](https://developer.apple.com/documentation/healthkit/)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks/)
- [WatchConnectivity](https://developer.apple.com/documentation/watchconnectivity/)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [RealityKit](https://developer.apple.com/documentation/realitykit/)
- [Metal](https://developer.apple.com/documentation/metal/)
