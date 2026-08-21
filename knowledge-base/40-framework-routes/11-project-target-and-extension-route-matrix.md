# Project, Target, Module, and Extension Route Matrix

## User outcome

Use this route when an idea has more than one app surface, platform, process, framework capability, or testing requirement. The goal is to choose a project shape that lets the feature grow without putting permission logic, AI sessions, persistence, or system-surface assumptions in the wrong target.

An Xcode project is a container for related products. A target describes one product to build. A Swift package target describes a module or test suite inside a package. A scheme selects targets, configurations, and execution details for a build action. These are different boundaries and should be recorded separately.

Apple’s Xcode documentation describes targets as products such as apps, frameworks, app extensions, and unit tests, and describes project-level settings as distinct from target-level settings. Xcode’s build system then assembles source files, resources, linked products, build settings, and phases into the product for the selected target. A folder tree alone is not evidence that the target graph, bundle, entitlement, or runtime route is correct.

## Start with a target graph

Draw the graph before creating folders:

~~~text
Workspace or project
├── MainApp target
│   ├── AppShell / SwiftUI surfaces
│   ├── Feature modules
│   ├── Domain and policy modules
│   └── Capability adapters
├── SharedKit package or framework target
│   ├── Domain models and use cases
│   ├── Typed feature contracts
│   └── Testable fakes and fixtures
├── System-surface targets
│   ├── Widget / Control / Live Activity
│   ├── App Intents or other extension target
│   └── Share / File / App Clip / notification surface where needed
├── Companion or platform targets
│   ├── watchOS app or extension
│   ├── visionOS app or spatial target
│   └── Mac Catalyst product configuration
└── Test targets and test plans
    ├── Domain and adapter tests
    ├── App UI tests
    ├── Extension/system-surface tests where supported
    └── Device/performance/accessibility test configurations
~~~

This is a planning shape, not a required number of targets. A small local-first iPhone utility may need only an app target and one test target. A widget, Live Activity, watch companion, or share extension creates another process and usually another bundle; that is a reason to define a projection and shared contract, not to copy the app’s entire view model into the extension.

## Boundary vocabulary

| Boundary | Owns | Does not prove |
| --- | --- | --- |
| Xcode project | Shared project settings, target list, references, and project-level configuration | That every target inherits the intended value or that the built artifact contains it |
| Xcode target | One product’s source/resource membership, build phases, linked products, settings, signing, capabilities, and bundle output | That a different target has the same capability, framework, resource, or entitlement |
| Swift package | Package manifest, products, module targets, resources, and package dependency graph | That every app/extension target can link or execute the package on every Apple platform |
| Module | A compile/import boundary and API surface | That the API is safe to call from an extension, background task, actor, or other process |
| Scheme | Build/run/test/profile/archive actions, selected targets, configurations, arguments, and environment | That another scheme or Release archive has the same inputs |
| Build configuration | A named set of settings such as Debug or Release, often layered with `.xcconfig` files | That a setting appears in the final bundle or entitlements without inspecting the product |
| App or extension bundle | A signed runtime product with its own identifier, resources, privacy manifest, and entitlements | That its host, account, service, hardware, or system surface will deliver the intended behavior |
| App Group | An explicitly registered shared container/keychain/IPC boundary for eligible targets | That arbitrary shared mutable state is synchronized, conflict-safe, private, or durable without a protocol |
| Test target/plan | Selected deterministic, UI, performance, or device test inputs | That excluded tests, unsupported hardware, system-owned UI, or production delivery were verified |

## Dependency direction

Prefer a one-way dependency graph:

~~~text
Domain / Policies
        ↑
Feature contracts and use cases
        ↑
Capability adapters and persistence implementations
        ↑
App, extension, companion, and system-surface compositions
~~~

The arrow means “depends on” when read from the top product surface downward. In practice:

- Domain types should not import SwiftUI, UIKit, WidgetKit, App Intents, StoreKit, or a concrete camera/session type merely to express business meaning.
- A feature module can depend on domain contracts and define a protocol for a capability adapter.
- An app target can provide the live adapter and SwiftUI composition.
- An extension can provide a smaller adapter or read a versioned projection from an App Group container.
- A test target can provide deterministic fakes and fixtures without linking a physical-device-only implementation unless the test specifically verifies that implementation.
- A system surface should invoke a shared use case or App Intent contract rather than duplicate the rule in a widget, Live Activity, notification action, or shortcut.
- Avoid cycles such as a shared module importing the app target, a widget importing the app’s SwiftUI shell, or a domain type storing an extension-only view value.

When a dependency is unavoidable, write down why it is target-safe, process-safe, actor-safe, and available on every platform that links it.

## Target selection matrix

| User outcome or capability | Smallest target shape | Shared boundary | Target-specific boundary | Proof to plan |
| --- | --- | --- | --- | --- |
| Main interactive iPhone/iPad app | iOS app target | Domain, feature state, services, SwiftUI components | Phone/pad navigation, input, scene, permissions, materials | Selected iOS scheme, simulator states, physical iPhone/iPad, accessibility and real capability |
| Mac app from an iPad app | iOS target with Mac Catalyst configuration, or a deliberate native macOS target | Domain/use cases and stable non-UI services | Catalyst/macOS menus, windows, pointer, keyboard, idiom, AppKit bridges | Run the actual Catalyst/macOS target on Mac; do not infer from iPad |
| Spatial UI or world interaction | Separate visionOS target or explicit multiplatform target route | Domain and reviewable state where meaningful | Windows, volumes, `RealityView`, immersive spaces, spatial input, comfort, safety | visionOS simulator plus Apple Vision Pro for spatial claims |
| Glanceable companion task | watchOS app target, with WatchConnectivity only if needed | Small domain projection and typed transfer contract | Watch UI, crown, short hierarchy, complications, notifications, Always On | Watch simulator sizes plus paired physical watch and transfer/system proof |
| Home Screen widget or Control | WidgetKit extension target | Versioned snapshot/projection and shared read service | Timeline/control configuration, extension process, refresh/action rules | Signed install, terminated-app and reload paths on a supported device |
| Live Activity | ActivityKit-capable app/extension arrangement | Codable attributes/content-state projection and action contract | Start/update/end/stale/privacy/push lifecycle | Physical device, entitlement/APNs/server state, expiration/recovery |
| App Shortcut or system invocation | App Intents code in the app or appropriate target | Shared use case, entities, authorization policy | Intent phrases, entity query, confirmation, system handoff | Invoke from the named system surface with signed target and account state |
| Share or file workflow | Share/File extension plus host app route | Transferable/FileDocument/domain import contract | Host lifecycle, security-scoped URL, provider/cancellation limits | Invoke from a real host app and inspect saved/imported result |
| App Clip | App Clip target plus full app handoff | Minimal route contract and durable handoff data | Size, invocation, Associated Domains, reduced feature set, handoff | Real invocation and full-app transition with configured domain/signing |
| Camera/audio/sensor feature | App target plus a capability adapter; extension only if the system route requires it | Typed capture event/proposal and permission state | Session queue, hardware, interruption, background, UI | Physical hardware, permissions, lifecycle interruption, thermal/battery spot check |
| On-device AI feature | App target plus isolated AI service/adapter and evaluation fixtures | Typed proposal/schema, provenance, prompt/model record | Model readiness, OS/device/language, review UI, cancellation | Representative device/language fixtures and physical-device model/latency proof |
| Paid feature or protected data | App target plus entitlement/authorization service | Deterministic entitlement/data policy | StoreKit/HealthKit/etc. UI, permissions, receipt/account state | Sandbox or real account plus signed target and server/system evidence |

## Xcode target configuration route

For each new target, capture this sequence:

1. **Name the product.** Record target type, platform, minimum deployment target, bundle identifier, executable/product name, and whether it is embedded in another product.
2. **Declare membership.** Decide which source files, resources, package products, privacy manifests, entitlements, and Info.plist values belong to this target. Target membership is not a cosmetic folder choice.
3. **Choose dependencies.** Add only the frameworks, packages, project targets, and embedded products the target actually uses. Verify build phases and dependency order.
4. **Choose the surface.** Add the correct SwiftUI, UIKit, WidgetKit, ActivityKit, App Intents, ExtensionKit, WatchKit, RealityKit, or other framework route for the product type. Do not link an app UI module into a background or extension target simply because it contains a convenient helper.
5. **Configure capabilities and permissions.** Map the feature’s permissions, entitlements, privacy manifest ownership, required-reason API declarations, App Group membership, and system capability to the exact target that uses them.
6. **Choose configurations.** Use Debug, Release, and any deliberate development/device/evaluation configuration. Store repeatable overrides in reviewed `.xcconfig` files when that improves inspection; avoid putting secrets in project settings or source.
7. **Choose schemes.** Create or edit a scheme that builds the intended target dependencies, uses the intended configuration, launches with explicit arguments/environment, and runs the intended test plan. The scheme is part of the evidence record.
8. **Build and inspect.** Build the exact target/scheme, inspect the generated bundle, and record the target name, SDK, deployment target, bundle identifier, version/build, linked products, embedded extensions, entitlements, Info.plist, privacy resources, and signing state.
9. **Run the right proof.** Promote the route from source review to preview, simulator, physical device, system host, paired device, signed distribution, or production evidence according to the claim.

## Swift package route

Use a local Swift package or framework target when a boundary is stable enough to compile and test independently. Swift Package Manager targets compile source files into modules or test suites, can depend on other targets or products, and scope resources to the target that owns them.

Recommended package layering:

~~~text
Sources/
  ProductDomain/       # models, policies, typed results; no UI
  ProductFeature/      # feature state/use cases/protocols
  ProductDesign/       # only if the UI module is genuinely reusable
  ProductAdapters/     # platform-gated implementations or protocols
  ProductFixtures/     # development-only fixtures if target-safe
Tests/
  ProductDomainTests/
  ProductFeatureTests/
~~~

Use target conditions and platform declarations deliberately. A package target that imports UIKit, AppKit, WatchKit, RealityKit, or a device-only framework is not automatically portable to every product target. Keep platform-specific code in a target or file boundary that the package manifest and the selected app target can actually resolve.

For external packages:

- Prefer a source-based dependency when it provides the needed behavior and its license, provenance, platform support, and maintenance fit the product.
- Choose a version requirement intentionally; branch and commit requirements are development or exceptional controls, not a substitute for dependency review.
- Commit the resolved package versions for team/reproducible builds where the project workflow expects it.
- Inspect binary dependencies and checksums; a package that resolves is not automatically trustworthy, portable, or App Store-ready.
- Add only the package products needed by each target. Do not make an extension depend on a package product that pulls in unsupported UI, network, or process assumptions.

## Extension and system-surface route

Treat every extension as a separate product with a host/process contract:

| Contract | Questions to answer |
| --- | --- |
| Host | Which app or system surface launches it? What does the host own? |
| Process | Can the main app be terminated? What state can the extension read without it? |
| Input | What action, intent, timeline, file, URL, or system event enters the extension? |
| Data | Is the input a snapshot, a shared container, a secure transfer, or a server record? |
| Side effect | What is allowed without reopening the app or asking for confirmation? |
| Lifetime | What can be initialized, cancelled, persisted, or retried before termination? |
| UI | Is the UI SwiftUI, UIKit, system-owned, or host-defined? |
| Proof | Which real host, device, account, entitlement, APNs environment, or pairing is required? |

App Groups can provide an explicitly registered shared container and related access for eligible targets. They do not turn multiple processes into one in-memory store. Define a versioned projection, atomic write/read rule, freshness timestamp, migration strategy, and conflict policy. Keep secrets and protected records inside the narrowest target/service boundary that can safely own them.

ExtensionKit can host custom extension UI and manage extension availability in supported host relationships. Follow the extension point’s documented contract; do not generalize an ExtensionKit custom UI route to WidgetKit, ActivityKit, Share extensions, or every system-owned surface. Each extension family has its own target template, lifecycle, resources, privacy, entitlements, host, and proof.

## Configuration and evidence matrix

| Evidence record | Inspect | Scope of claim |
| --- | --- | --- |
| Source record | Official framework/API, target availability, HIG/system-surface guidance | The route is documented and worth evaluating |
| Project record | Target graph, target membership, package products, linked frameworks, build phases | The project declares the intended architecture |
| Configuration record | Deployment target, `.xcconfig`, Debug/Release settings, scheme/test-plan mapping | The selected build action has known inputs |
| Build record | Successful selected target/scheme, warnings, compiler/linker output | That configuration built for a destination |
| Bundle record | Product bundle, embedded extensions, Info.plist, privacy manifest, entitlements, signing | The generated artifact contains the intended metadata |
| Simulator/preview record | UI states, navigation, deterministic data, adaptation | Controlled rendering or simulated behavior |
| Physical/system record | Hardware, permissions, accessibility, system host, paired device, APNs/account/service | The named runtime capability behaved in the named environment |
| Distribution record | Archive validation, signing, TestFlight/App Store submission metadata | The artifact passed that distribution boundary |
| Production record | Published version, server/account/entitlement/system delivery, live task | The exact deployed claim was observed |

Never summarize these as “the app works” without naming the target, configuration, destination, system surface, and evidence layer.

## Sources

- [Configuring a new target in your project](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [ExtensionKit](https://developer.apple.com/documentation/extensionkit)
- [Including extension-based UI in your interface](https://developer.apple.com/documentation/extensionkit/including-extension-based-ui-in-your-interface)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Security entitlements](https://developer.apple.com/documentation/bundleresources/security-entitlements)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
