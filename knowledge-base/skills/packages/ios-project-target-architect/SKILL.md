---
name: ios-project-target-architect
description: Architect or audit an Apple-platform project before implementation by choosing the correct Xcode targets, Swift modules and packages, extensions, schemes, configurations, capabilities, privacy resources, test plans, and evidence gates for a feature. Use when an iOS/iPadOS/watchOS/macOS/visionOS/CarPlay/App Clip/widget/Live Activity/companion feature needs a target-aware build route or when project structure and proof are unclear.
---

# iOS Project, Target, and Module Architect

Shape the project around the user outcome and the Apple surface that owns it. Keep shared domain truth separate from target-specific process, UI, lifecycle, entitlements, and proof.

`outcome -> target graph -> module graph -> capability/configuration -> surface lifecycle -> executable evidence`

## Read before acting

- Inspect the real repository and preserve existing dirty work. Locate the `.xcodeproj` or `.xcworkspace`, `Package.swift` files, schemes, build configurations, deployment targets, supported destinations, target membership, source/resource folders, entitlements, `Info.plist` files, privacy manifests, extensions, App Groups, tests, fixtures, and generated artifacts.
- Read the [project-shape foundation](../../../00-foundations/03-project-shape-and-module-boundaries.md), [target and extension route matrix](../../../40-framework-routes/11-project-target-and-extension-route-matrix.md), [Xcode target/module plan](../../../90-templates/xcode-target-and-module-plan.md), [target-aware feature scaffold](../../../90-templates/target-aware-feature-scaffold.md), and [configuration/artifact checklist](../../../60-verification/06-target-configuration-and-artifact-checklist.md).
- Refresh the exact official Apple or Swift page for any API, target type, platform condition, entitlement, privacy requirement, build setting, or system surface you intend to use. Mark unresolved symbols or availability as `to-verify`; do not infer them from a framework name.

## Route workflow

1. Write the outcome, entry point, primary action, accepted result, failure consequence, offline requirement, privacy sensitivity, supported platforms, and whether the feature must run in the app, an extension, a companion, or a system-owned surface.
2. Inventory the existing project before proposing a target. Record project/workspace, app targets, framework or library targets, package products, extensions, tests, schemes, configurations, bundle identifiers, deployment targets, resources, entitlements, privacy manifests, and App Groups.
3. Draw a target graph. For every target, record platform/device family, process/host, bundle identifier, source and resource membership, linked products, capabilities, signing identity, lifecycle, and the evidence needed to prove it. Put dependencies in one direction: target-specific surface -> shared feature/domain modules -> platform adapters -> system frameworks.
4. Draw a module graph. Keep models, deterministic domain rules, persistence protocols, and feature use cases in shared modules. Keep SwiftUI screens, extension entry points, lifecycle delegates, OS-specific adapters, entitlements, and process-only state at the owning target boundary.
5. Select the narrowest target route:
   - Put ordinary UI, navigation, persistence, and feature orchestration in the main app target unless another process or system-owned entry point is required.
   - Use a framework or Swift package product for reusable domain, feature, or platform-adapter code with a clear dependency boundary.
   - Use an app extension only when the host/system invokes it; identify its host, extension point, process lifecycle, shared data route, and unavailable APIs.
   - Use WidgetKit, ActivityKit, App Intents, Share, File Provider, App Clip, watchOS, CarPlay, visionOS, or another companion/system target only when the user outcome requires that surface. Do not create a target merely to organize files.
6. Route dependencies. Prefer source package products when the source boundary is appropriate; inspect binary package products separately. Record minimum platform versions, product names, resource handling, transitive dependencies, license/provenance notes, and whether each target actually links the product.
7. Map the capability configuration. For each target, identify entitlements, capability toggles, usage descriptions, background modes, associated domains, App Groups, privacy manifest declarations, account/service setup, and protected-data boundaries. Put a requirement on the owning target and record the smallest verification action.
8. Map schemes and configurations. Identify Debug, test, preview/fixture, profile, and Release purposes; use `.xcconfig` files for intentional shared settings; make scheme actions and test-plan selection explicit. Never hide a target or entitlement change in an undocumented local setting.
9. Build the feature handoff: `surface input -> adapter or framework operation -> normalized evidence/proposal -> deterministic validation -> shared domain/use case -> persistence or side effect -> derived target/system presentation`.
10. Model lifecycle and failure states before implementation: unavailable, denied, restricted, not configured, loading, partial, stale, interrupted, cancelled, backgrounded, process-recreated, expired, conflict, and completed. Define start/stop/cancel/retry behavior and a fallback that does not pretend the capability succeeded.
11. If implementation is requested, create the smallest target/module slice that satisfies the outcome. Preserve the existing project shape, avoid circular dependencies, and keep system/extension entry points thin. If only planning or audit was requested, stop after producing the route and verification ledger.
12. Verify proportionally and report evidence by boundary: source, compile, unit/UI test, preview/fixture, simulator, physical device, two-device/accessory/vehicle, system invocation, signed artifact, TestFlight/App Store, and production. Record device, OS, build, target, configuration, task, result, and artifact path for each claim.

## Target selection matrix

| Requirement | First route to evaluate | Boundary to record |
| --- | --- | --- |
| iPhone/iPad app UI | App target with SwiftUI/UIKit as needed | Device family, deployment target, navigation, resources, entitlements |
| Reusable feature/domain | Swift package or framework target | Public API, product dependency, resources, platform conditions |
| Widget or control | WidgetKit extension target | Timeline/control lifecycle, App Group or intent data, widget-family proof |
| Live status | ActivityKit-enabled app/extension route | Activity attributes/content state, start/update/end ownership, device proof |
| Siri/Shortcuts/Spotlight action | App Intents types plus app target | `AppIntent`, entities/queries, authentication, donation/shortcut/system proof |
| Share or file workflow | Share/File Provider extension | Host contract, security-scoped data, extension timeout/process proof |
| App Clip | App Clip target | Associated domain, invocation, limited data/auth route, signed artifact proof |
| Watch or companion | watchOS target plus WatchConnectivity when needed | Reachability, transfer semantics, paired-device proof |
| CarPlay or vehicle UI | CarPlay scene/extension route | Entitlement, template ownership, connected-vehicle proof |
| macOS/Catalyst/visionOS | Separate target or explicit multiplatform target | API availability, conditional code, input/layout, destination proof |
| Background work | BackgroundTasks or system-owned scheduling | Registration, permitted task type, cancellation/expiration, scheduled-run proof |
| Protected data or accessory | Main target plus owning framework/capability | Authorization, usage text, hardware, pairing, privacy, physical proof |

## Module-boundary rules

- Make shared code describe product truth and deterministic behavior, not a particular scene, extension host, or device process.
- Inject persistence, networking, clock, model, location, media, and system clients behind protocols where tests need deterministic fixtures.
- Keep target-specific adapters responsible for OS availability, authorization, lifecycle, and conversion into shared values or proposals.
- Keep side effects behind explicit use cases. Require validation, authorization, confirmation, idempotency, and conflict handling before a target invokes a consequential operation.
- Prefer one-way dependencies. A package should not import an app target; an extension should not reach into in-memory app state; a shared module should not own an entitlement.
- Treat an App Group as a deliberate shared-container contract, not proof that two processes share memory. Define schema, migration, coordination, retention, and failure behavior.
- Use `#if os(...)` and availability checks where required, but keep platform-specific behavior observable through tests or target-specific verification rather than scattering conditions through domain code.

## Configuration and proof ledger

For each target, fill this minimum record:

| Field | Record |
| --- | --- |
| Identity | Target name, product, bundle ID, platform/device family, deployment target |
| Inputs | Sources, resources, package products, linked frameworks, generated files |
| Process | Host, extension point, lifecycle, background/system invocation |
| Configuration | Schemes, configurations, `.xcconfig`, signing, capabilities, entitlements |
| Privacy | Usage descriptions, privacy manifest, App Group/data scope, retention/deletion |
| Tests | Test targets/plans, fixtures, accessibility, performance, route-specific checks |
| Evidence | Exact build/device/system/artifact claim, environment, date, result, next gap |

Do not report “builds,” “works on device,” “the widget/extension/system route works,” “the entitlement is active,” or “release-ready” until the matching evidence exists. Documentation establishes an API route; it does not establish compilation, signing, authorization, physical hardware behavior, system delivery, or App Review approval.

## Handoff format

Return these artifacts in the project or knowledge base:

1. A target graph with owners, processes, products, dependencies, and system/extension boundaries.
2. A module graph with public interfaces, platform adapters, resource ownership, and rejected dependencies.
3. A target configuration ledger for capabilities, entitlements, privacy, App Groups, schemes, configurations, and test plans.
4. A feature scaffold mapping input to normalized evidence, deterministic validation, domain use case, persistence/side effect, and target-specific presentation.
5. A verification ledger that names the next smallest compile, test, simulator, physical-device, system, or artifact check.

## Refuse to assume

- Do not add an account, backend, cloud sync, analytics, paid service, credential, background mode, protected-data capability, or new target without a product need and authorization.
- Do not copy Apple-owned screens, branding, icons, wording, or proprietary visual identity; use documented native behavior with original product hierarchy and copy.
- Do not claim that a target exists, a package product links, an entitlement is active, an extension is invoked, a system surface is delivered, or a release is ready from source text alone.
- Do not use a preview or simulator as proof of camera, microphone, sensors, haptics, radio, GPU/thermal behavior, Apple Intelligence, Watch, CarPlay, App Clip, protected data, or production delivery.

## Workspace routes

- [Knowledge-base map](../../../README.md)
- [Project and target route matrix](../../../40-framework-routes/11-project-target-and-extension-route-matrix.md)
- [Xcode target/module plan](../../../90-templates/xcode-target-and-module-plan.md)
- [Target-aware feature scaffold](../../../90-templates/target-aware-feature-scaffold.md)
- [Target configuration and artifact checklist](../../../60-verification/06-target-configuration-and-artifact-checklist.md)
- [Capability route planner](../ios-capability-route-planner/SKILL.md)

## Sources

- [Configuring a new target](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Customizing build schemes](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Adding package dependencies](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Swift packages in Xcode](https://developer.apple.com/documentation/xcode/swift-packages)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Swift Package Manager targets](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [ExtensionKit](https://developer.apple.com/documentation/extensionkit)
- [Including extension-based UI](https://developer.apple.com/documentation/extensionkit/including-extension-based-ui-in-your-interface)
- [App Groups entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Security entitlements](https://developer.apple.com/documentation/bundleresources/security-entitlements)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding tests to an Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Organizing tests with test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [WatchConnectivity](https://developer.apple.com/documentation/watchconnectivity/)
- [CarPlay](https://developer.apple.com/documentation/carplay)
