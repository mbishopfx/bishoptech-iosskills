# Target Configuration and Artifact Checklist

Use this checklist when a feature crosses an app target, Swift package, extension, companion target, system surface, or Release archive. It verifies configuration and evidence boundaries; it does not replace compiling the selected project or testing the named device/system route.

## 1. Source and route identity

- [ ] The user outcome is written in plain language.
- [ ] The selected Apple framework, exact symbol/API route, and target family are recorded.
- [ ] The current Apple Developer or Swift source is linked and its availability/beta/deprecation note is captured.
- [ ] The smallest standard SwiftUI/UIKit/system-surface route was considered before a custom bridge or new target.
- [ ] The HIG surface and expected input model were checked for each claimed platform.
- [ ] The evidence claim is scoped: source, project, build, preview, simulator, physical device, system host, signed distribution, server/account, or production.

## 2. Project and target graph

- [ ] The project/workspace contains the intended app, framework/package, extension, companion, and test targets only.
- [ ] Each target has a named product type, platform, minimum OS, bundle identifier, process/host, and owner.
- [ ] Target membership matches the intended source and resource ownership.
- [ ] The app does not accidentally include extension-only code, test-only code, or development fixtures.
- [ ] Extensions and companions do not import the main app target or rely on its in-memory process.
- [ ] Target dependencies and Build Phases target order are explicit where Xcode cannot infer them.
- [ ] Embedded products, copy phases, frameworks, package products, and resource bundles are inspected for the selected target.
- [ ] A shared module’s public API is target-safe, platform-safe, actor-safe, and process-safe for every consumer.
- [ ] The dependency graph has no cycle hidden by a convenience target, global singleton, or shared UI module.

## 3. Swift packages and binary dependencies

- [ ] Each package product is added only to the targets that need it.
- [ ] Package platform declarations and target conditions match the app, extension, companion, and test destinations.
- [ ] Source-based versus binary dependencies are recorded.
- [ ] Binary dependencies have provenance and checksum review.
- [ ] Version/range/branch/commit requirements are intentional and documented.
- [ ] `Package.resolved` is present and handled according to the team’s reproducibility policy.
- [ ] Package resources are scoped to the target that owns them and are available from the selected consumer.
- [ ] Swift Testing/XCTest remains in test targets and is not distributed through an app product.
- [ ] A local package override is labeled as development state and has a return-to-versioned-dependency plan.

## 4. Build settings and configurations

- [ ] The target SDK, deployment target, supported destinations, architecture, and device family are recorded.
- [ ] Debug, Release, and any evaluation/device configurations are named with their purpose.
- [ ] `.xcconfig` files are target/project-owned intentionally, included in the expected configuration, and not embedded as accidental bundle resources.
- [ ] Inherited project settings versus target overrides are reviewed.
- [ ] API availability, feature flags, and custom Swift compilation conditions are recorded.
- [ ] Secrets are not present in source, `.xcconfig`, launch arguments, or committed project settings.
- [ ] Release settings do not inherit development mocks, debug logging payloads, local endpoints, or test credentials.
- [ ] The selected scheme identifies the intended targets, configuration, destination, arguments, environment, and test plan.
- [ ] Archive/distribution uses the intended Release configuration rather than a convenient development scheme.

## 5. Capabilities, entitlements, and privacy resources

- [ ] Every permission maps to the target that requests it and has purpose-specific Info.plist text.
- [ ] Every entitlement/capability is enabled on the exact target that needs it.
- [ ] App Groups list only the eligible targets and have a documented versioned projection/read-write protocol.
- [ ] Keychain access groups, associated domains, push, HealthKit, WeatherKit, HomeKit, NFC, Apple Pay, App Attest, and other sensitive capabilities are target-specific and account/team-specific.
- [ ] `PrivacyInfo.xcprivacy` ownership is defined for the app, framework, SDK, widget, and extension bundles that use required-reason APIs or declare data practices.
- [ ] Privacy manifest entries, permission copy, App Store privacy answers, data retention, tracking domains, and observed behavior reconcile.
- [ ] The built artifact—not only the source project—was inspected for entitlements, Info.plist, privacy manifests, embedded bundles, and identifiers.
- [ ] The target’s signing team, provisioning profile, application identifier, and capability entitlements are consistent.

## 6. Extension and system-surface boundaries

- [ ] The host/system entry point is named: widget, control, Live Activity, App Intent, Share, File Provider, App Clip, notification, Watch, CarPlay, ExtensionKit, or another route.
- [ ] The extension’s process/lifetime limits and input/output contract are documented.
- [ ] The extension can render or act when the main app process is terminated, or the limitation is represented honestly.
- [ ] Shared data includes version, freshness, migration, deletion, conflict, and stale/error behavior.
- [ ] Deep links and handoffs validate destination identity and authorization before navigating or applying a side effect.
- [ ] System-owned UI is invoked through the documented API rather than imitated inside the app.
- [ ] Widget timelines/reloads, Live Activity updates, App Intent invocation, notifications, or extension host behavior are tested outside the main app screen.
- [ ] APNs, server, account, pairing, vehicle, or host state is recorded when the surface depends on it.

## 7. Test targets and plans

- [ ] Unit tests cover domain/policy and deterministic adapter mapping without requiring hardware.
- [ ] Integration tests cover persistence, migration, package/module boundaries, and fake capability services.
- [ ] UI tests cover navigation, sheets, focus, keyboard, state restoration, deep links, and accessibility identifiers.
- [ ] System-surface/device tests are separated from deterministic tests by target, test plan, tag, or configuration.
- [ ] The active `.xctestplan` lists the intended test targets, configurations, destinations, and included/excluded tags.
- [ ] The focused development plan and broader pre-submission plan are distinct when their scopes differ.
- [ ] Test results record skipped/excluded tests and explain why they do not weaken the claim.
- [ ] Performance tests record device, OS, build configuration, workload, warm/cold state, and metric.
- [ ] AI/model/device-dependent tests record OS, model/asset/language state, prompt/schema/tool version, and representative fixtures.

## 8. Runtime evidence

| Claim | Minimum named evidence | Do not substitute |
| --- | --- | --- |
| Source/API route is valid | Current official source and selected SDK inspection | A remembered symbol name |
| Target builds | Exact scheme/configuration/destination build result | A different target or preview |
| UI state renders | Preview or simulator fixture | A physical hardware claim |
| App logic is correct | Deterministic unit/integration result | A screenshot |
| Accessibility task works | Actual target task with relevant assistive technology | Accessibility identifiers alone |
| Camera/audio/sensor/haptic behavior works | Physical device with permission and lifecycle conditions | Simulator/mock only |
| On-device AI is available/usable | Named physical device, OS, model/language/assets, representative fixtures | “Apple Intelligence capable” label or simulator |
| Widget/Live Activity/Control/App Intent works | Signed artifact and actual system-surface invocation/update state | Main app screen or local unit test |
| Watch/CarPlay/visionOS behavior works | Named paired/physical/system target | iPhone/iPad simulator |
| Release configuration is correct | Validated intended Release archive and artifact inspection | Debug build or TestFlight metadata alone |
| Production behavior is correct | Published version plus live server/account/system observation | Successful archive or upload |

## 9. Artifact inspection record

Fill this after building the selected product:

- Project/workspace:
- Scheme:
- Configuration:
- Target:
- SDK and deployment target:
- Destination/device and OS:
- Bundle identifier/version/build:
- Embedded extensions and bundle identifiers:
- Linked frameworks/package products:
- `Info.plist` and usage descriptions:
- Entitlements:
- Privacy manifests:
- Signing/provisioning state:
- Test plan/result bundle:
- Warnings/errors:
- Expected versus observed behavior:
- Remaining unverified claims:

## 10. Stop conditions

Pause the release claim and return to the project/configuration route when:

- the selected scheme does not build the target that the claim names;
- a framework works only in a different target or platform configuration;
- a required entitlement, permission description, App Group, privacy manifest, package product, or embedded extension is missing from the artifact;
- the main app process is assumed to be alive for an extension/system surface;
- a source, simulator, preview, or signed archive is being used to claim physical hardware, system delivery, accessibility task completion, account/server behavior, or production success;
- the project contains secrets or environment-specific values that cannot be traced to an intentional configuration boundary;
- the target’s Release archive has not been inspected after the last target, package, entitlement, privacy, or version change.

## Sources

- [Configuring a new target in your project](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Build system](https://developer.apple.com/documentation/xcode/build-system)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding a build configuration file to your project](https://developer.apple.com/documentation/xcode/adding-a-build-configuration-file-to-your-project)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Identifying binary dependencies](https://developer.apple.com/documentation/xcode/identifying-binary-dependencies)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [ExtensionKit](https://developer.apple.com/documentation/extensionkit)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Security entitlements](https://developer.apple.com/documentation/bundleresources/security-entitlements)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Preparing your app for distribution](https://developer.apple.com/documentation/xcode/preparing-your-app-for-distribution)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
