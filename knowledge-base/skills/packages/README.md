# Workspace Skill Packages

These are reusable, workspace-scoped Codex skill packages for the iOS 26 knowledge base. They turn the source-linked blueprints into task instructions without installing or mutating global Codex configuration.

Use the [public skill catalog](../../../docs/skills-catalog.md) for a role-by-role explanation of each package, its features, expected output, and handoff.

Use the package that matches the work:

- [SwiftUI native design](swiftui-native-design/SKILL.md) for adaptive SwiftUI screens, components, navigation, previews, and accessibility.
- [Liquid Glass design](liquid-glass-design/SKILL.md) for system-first Liquid Glass adoption and custom glass effects.
- [On-device AI feature](on-device-ai-feature/SKILL.md) for Foundation Models, Vision, Core ML, Speech, Translation, Natural Language, and safe reviewable intelligence flows.
- [Apple SDK route](apple-sdk-route/SKILL.md) for turning an app idea into a framework, state, permission, entitlement, and verification plan.
- [iOS capability route planner](ios-capability-route-planner/SKILL.md) for outcome-first Apple SDK selection, native/Liquid Glass surfaces, on-device AI boundaries, lifecycle/fallback contracts, and proportional proof planning.
- [iOS project, target, and module architect](ios-project-target-architect/SKILL.md) for target graphs, module/package boundaries, extensions, schemes/configurations, capabilities, privacy resources, test plans, and artifact-proof planning.
- [iOS system surfaces and background](ios-system-surfaces-and-background/SKILL.md) for documents, PhotosUI, WebKit/PDF, sharing, extensions, widgets, Live Activities, App Groups, and BackgroundTasks.
- [iOS companion and communications](ios-companion-communications/SKILL.md) for WatchConnectivity, CarPlay, App Clips, CallKit, LiveCommunicationKit, PushKit, APNs, and UserNotifications.
- [iOS device and release proof](ios-device-release-proof/SKILL.md) for separating source, compile, simulator, physical-device, signed, system-surface, TestFlight, App Store, and production evidence.
- [iOS media, ML, and physical inputs](ios-media-ml-and-inputs/SKILL.md) for AVKit/AVFoundation, Core Image, VideoToolbox, Vision, Core ML, Natural Language, Core NFC, MusicKit, ShazamKit, provenance, bounded processing, privacy, and physical-device performance proof.
- [iOS spatial, graphics, and games](ios-spatial-graphics-and-games/SKILL.md) for ARKit, RealityKit, visionOS RealityView and ImmersiveSpace, Metal, SpriteKit, GameplayKit, GameKit, deterministic state, accessibility, and physical-device performance proof.
- [iOS native design and Liquid Glass verification](ios-native-design-verification/SKILL.md) for HIG hierarchy, SwiftUI state/adaptation, system-first Liquid Glass, semantic controls, Dynamic Type, reduced motion/effects, accessibility, haptics, and visual/physical-device proof.
- [iOS data and device services](ios-data-and-device-services/SKILL.md) for SwiftData, CloudKit, HealthKit, Contacts, EventKit, WeatherKit, HomeKit, Core Bluetooth, Nearby Interaction, Network/Bonjour, privacy, sync/conflicts, and physical-device proof.
- [iOS commerce, identity, and security](ios-commerce-identity-and-security/SKILL.md) for StoreKit 2, PassKit Apple Pay and Wallet, Sign in with Apple, Keychain, LocalAuthentication, CryptoKit, DeviceCheck, App Attest, URLSession/Network, server trust, privacy, and release proof.
- [iOS on-device intelligence evaluation](ios-on-device-intelligence-evaluation/SKILL.md) for Foundation Models, Vision, Core ML, Speech, Translation, Natural Language, Sound Analysis, App Intents, availability, typed output, tool safety, evaluation, fallback, privacy, and physical-device proof.
- [iOS privacy, performance, and release proof](ios-privacy-performance-release-proof/SKILL.md) for PrivacyInfo.xcprivacy, required-reason APIs, Swift Testing/XCTest test plans, OSLog/signposts/MetricKit, accessibility task evidence, system surfaces, archive validation, TestFlight, App Store Connect, and release boundaries.
- [iOS testing and release assurance](ios-testing-and-release-assurance/SKILL.md) for Swift Testing, XCTest/XCUIAutomation, accessibility audits/tasks, Liquid Glass regression, on-device AI evaluation, performance, physical/system evidence, archives, and TestFlight gates.
- [iOS source refresh and availability maintenance](ios-source-refresh-and-availability/SKILL.md) for official-source/SDK drift, availability and entitlement audits, affected-route graph updates, recipe/package validation, live URL checks, and portable bundle refresh receipts.
- [Agentic Apple engineering team](ios-agentic-apple-engineering-team/SKILL.md) to orchestrate the specialist roles into a source-grounded, testable, audit-ready native Apple development workflow for LLMs and solo developers.

Packaged artifacts:

- [SwiftUI native design `.skill`](../dist/swiftui-native-design.skill)
- [Liquid Glass design `.skill`](../dist/liquid-glass-design.skill)
- [On-device AI feature `.skill`](../dist/on-device-ai-feature.skill)
- [Apple SDK route `.skill`](../dist/apple-sdk-route.skill)
- [iOS capability route planner `.skill`](../dist/ios-capability-route-planner.skill)
- [iOS project, target, and module architect `.skill`](../dist/ios-project-target-architect.skill)
- [System surfaces and background `.skill`](../dist/ios-system-surfaces-and-background.skill)
- [Companion communications `.skill`](../dist/ios-companion-communications.skill)
- [Device and release proof `.skill`](../dist/ios-device-release-proof.skill)
- [Media, ML, and physical inputs `.skill`](../dist/ios-media-ml-and-inputs.skill)
- [Spatial, graphics, and games `.skill`](../dist/ios-spatial-graphics-and-games.skill)
- [Native design and Liquid Glass verification `.skill`](../dist/ios-native-design-verification.skill)
- [Data and device services `.skill`](../dist/ios-data-and-device-services.skill)
- [Commerce, identity, and security `.skill`](../dist/ios-commerce-identity-and-security.skill)
- [On-device intelligence evaluation `.skill`](../dist/ios-on-device-intelligence-evaluation.skill)
- [Privacy, performance, and release proof `.skill`](../dist/ios-privacy-performance-release-proof.skill)
- [Testing and release assurance `.skill`](../dist/ios-testing-and-release-assurance.skill)
- [Source refresh and availability `.skill`](../dist/ios-source-refresh-and-availability.skill)
- [Agentic Apple engineering team `.skill`](../dist/ios-agentic-apple-engineering-team.skill)

## Package contract

Every package must:

- inspect the target project and deployment target before changing implementation;
- refresh the relevant official Apple or Swift sources when APIs, availability, or platform behavior matter;
- route uncertain decisions back to the [knowledge-base map](../../README.md) and its source registry;
- keep generated suggestions, system availability, permission state, and committed domain truth distinct;
- state what preview, simulator, physical-device, and release evidence can actually prove;
- preserve the user’s supplied copy, assets, privacy boundary, and requested scope.

These packages are instructions, not proof that any target app compiles, runs on a physical device, passes review, or behaves identically across Apple Intelligence configurations.

## Related blueprints

- [SwiftUI native design blueprint](../swiftui-native-design.md)
- [Liquid Glass design blueprint](../liquid-glass-design.md)
- [On-device AI feature blueprint](../on-device-ai-feature.md)
- [Apple SDK route blueprint](../apple-sdk-route.md)

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
