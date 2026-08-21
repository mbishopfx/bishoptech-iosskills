# Xcode Target and Module Plan

Use this before creating or reshaping an Xcode project. Fill the plan from the user outcome and the selected Apple route. A completed plan records intended configuration; it does not prove that Xcode can build the project or that the runtime capability works.

## Product outcome

- Person and context:
- One-sentence outcome:
- Primary platform(s): iOS, iPadOS, Mac Catalyst, macOS, visionOS, watchOS, or another named target:
- Main app target needed? Why or why not:
- System/companion surfaces needed:
- What must remain local/on device:
- What may cross a process, device, or network boundary:

## Target inventory

Add one row for every product and test target. Do not collapse app, extension, companion, framework, and test bundles into a single row.

| Target | Product/type | Platform + minimum OS | Bundle identifier | Process/host | Product embeds or consumes it | Target-specific UI/frameworks |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

### Target-specific configuration

For each row, record:

- Source-file target membership:
- Resource membership:
- Linked frameworks and package products:
- Copy/embed phases:
- Target dependencies and build order:
- `Info.plist` ownership and required usage descriptions:
- `PrivacyInfo.xcprivacy` ownership and included bundle:
- Capabilities and entitlements:
- App Group identifiers, if any:
- Signing team/profile/certificate strategy:
- Supported device family and input modes:
- Extension/system host or paired device:
- Known unavailable/fallback states:

## Module graph

Draw dependencies from product surfaces toward reusable contracts:

~~~text
Domain / policies
  ↓
Feature contracts / use cases
  ↓
Capability adapters / persistence / transport
  ↓
App and system-surface compositions
~~~

| Module/package target | Public API purpose | Imports/frameworks | Depends on | Used by | Platform condition | Test target |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

Check the graph:

- [ ] Domain models and policies do not import a view or app target.
- [ ] Feature modules expose typed state/use-case contracts rather than controller instances.
- [ ] Capability adapters own framework lifecycle, permissions, cancellation, and error mapping.
- [ ] Platform-specific UI is in the target or module that can actually compile for that platform.
- [ ] Extensions do not depend on the main app process or its in-memory state.
- [ ] Test targets depend on the smallest module they can test directly.
- [ ] No dependency cycle is hidden by a convenience import or a shared singleton.

## Framework route record

For every selected capability, complete one row:

| User outcome | Framework/symbol seam | Owning target | Permission | Entitlement/capability | Device/service/account state | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

Record the lifecycle explicitly:

- Start trigger:
- Active state:
- Cancellation trigger:
- Teardown/reset route:
- Background/scene transition behavior:
- Backpressure or resource limit:
- Stale/late result policy:
- Normalized domain output:
- Human review or deterministic validation step:
- Side effect and approval boundary:

## Swift package and dependency plan

- Package name and repository:
- Local package or remote dependency:
- Product(s) imported by each target:
- Version/range/branch/commit requirement:
- `Package.resolved` ownership and review:
- Source versus binary dependency:
- Binary provenance/checksum review:
- Supported platforms and deployment targets:
- Package resources and localization:
- Test-only dependencies:
- Removal/rollback plan:

Check:

- [ ] The package target owns the source and resources it compiles.
- [ ] Test frameworks terminate in test targets and are not distributed through an app product.
- [ ] Every target receives only the package products it needs.
- [ ] Package platform conditions are compatible with every target that links the product.
- [ ] The dependency’s source, license, binary contents, checksum, and update policy were reviewed.

## Build configurations and schemes

| Configuration | Purpose | `.xcconfig` | API/feature flags | Signing | Data/service environment | Test plan |
| --- | --- | --- | --- | --- | --- | --- |
| Debug |  |  |  |  |  |  |
| Release |  |  |  |  |  |  |
| Evaluation/device, if needed |  |  |  |  |  |  |

| Scheme | Build targets | Run destination | Build configuration | Launch arguments/environment | Test plan | Archive/distribution use |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

Check:

- [ ] The scheme builds all required target dependencies in the intended order.
- [ ] The scheme names the active configuration and destination.
- [ ] Launch arguments and environment are non-secret and reproducible.
- [ ] Debug-only mocks or feature flags cannot silently enter Release.
- [ ] The archive scheme is separate from a development scheme when their evidence differs.
- [ ] The active test plan, configurations, destinations, and included/excluded tags are recorded.

## System-surface and shared-data plan

| Surface | Target/host | Entry event | Input projection | Shared data boundary | Output/deep link | Freshness/termination rule |
| --- | --- | --- | --- | --- | --- | --- |
| Widget/control |  |  |  |  |  |  |
| Live Activity |  |  |  |  |  |  |
| App Intent/Shortcut |  |  |  |  |  |  |
| Share/file/App Clip |  |  |  |  |  |  |
| Watch/CarPlay/other companion |  |  |  |  |  |  |

If using an App Group:

- Group identifier:
- Members:
- Versioned records/projections:
- Atomic write/read strategy:
- Conflict and last-writer policy:
- Migration/deletion behavior:
- Sensitive data allowed in the group:
- What happens when one member is missing, terminated, outdated, or unauthorized:

## UI and platform composition

- Shared domain state:
- iPhone surface:
- iPad surface:
- Mac Catalyst/macOS surface:
- visionOS surface:
- watchOS surface:
- UIKit/AppKit/WatchKit representable seam, if any:
- System-owned surface used before custom UI:
- Liquid Glass functional group and fallback:
- Dynamic Type/localization/right-to-left plan:
- Touch/pointer/keyboard/Pencil/eyes-hands/crown paths:
- VoiceOver/Voice Control/Switch Control/Assistive Access path:

## Verification ledger

| Evidence layer | Target/configuration | Scenario | Expected record | Actual result/link |
| --- | --- | --- | --- | --- |
| Official source |  |  |  |  |
| Project/target inspection |  |  |  |  |
| Build |  |  |  |  |
| Preview |  |  |  |  |
| Simulator/UI test |  |  |  |  |
| Physical device |  |  |  |  |
| System host/paired device |  |  |  |  |
| Signed archive/distribution |  |  |  |  |
| Production/server/account |  |  |  |  |

The final claim must be no broader than the strongest completed row. A package graph, green unit test, preview, simulator run, or signed archive cannot silently stand in for a physical capability, system-surface, account, server, accessibility, or production claim.

## Sources

- [Configuring a new target in your project](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
