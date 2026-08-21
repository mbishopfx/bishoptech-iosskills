# Source Review Checklist

Use before implementing a version-sensitive feature. When the feature crosses targets, packages, extensions, companions, or system surfaces, pair it with the [target configuration and artifact checklist](06-target-configuration-and-artifact-checklist.md).

## Source identity

- [ ] The primary framework page is official Apple documentation.
- [ ] The exact API/article/sample page is linked.
- [ ] The SDK/OS assumption is recorded.
- [ ] The page was checked recently enough for this project.
- [ ] Beta/deprecated/future-software notes are recorded.

## Behavior

- [ ] The user outcome is stated in plain language.
- [ ] The smallest Apple-native route is identified.
- [ ] Availability and device requirements are explicit.
- [ ] Permission and entitlement requirements are explicit.
- [ ] Lifecycle and cancellation behavior are understood.
- [ ] Error/unavailable behavior is part of the design.

## Design

- [ ] Standard SwiftUI/UIKit components were considered first.
- [ ] HIG guidance was checked for the relevant surface.
- [ ] Dynamic Type, accessibility, color, contrast, and motion behavior are named.
- [ ] Liquid Glass is used only where it clarifies a functional layer.

## Evidence

- [ ] The implementation evidence needed is listed.
- [ ] Preview evidence is separated from runtime evidence.
- [ ] Simulator evidence is separated from physical-device evidence.
- [ ] Release/App Store evidence is separated from local build evidence.

## Privacy and policy-sensitive APIs

- [ ] The feature’s use of `PrivacyInfo.xcprivacy` is identified separately from `Info.plist` permission text and target entitlements.
- [ ] Every required-reason API category used by app code and each third-party SDK is mapped to the exact approved reason value from Apple’s current documentation.
- [ ] Collected data, tracking domains, retention, linkage, and remote processing are recorded from the actual implementation rather than inferred from the framework name.
- [ ] The archive privacy report and App Store Connect App Privacy answers have an explicit reconciliation step.
- [ ] Any preliminary, beta, deprecated, or future-OS API is labeled with its deployment-target strategy and fallback.

## Testing and performance evidence

- [ ] The test type matches the claim: Swift Testing/XCTest for deterministic logic, XCUIAutomation for UI flows, accessibility audits for diagnostics, and physical/system tests for protected or hardware behavior.
- [ ] The active `.xctestplan`, included/excluded tags, configurations, destinations, and command are recorded.
- [ ] Performance baselines name the device, OS, build configuration, workload, warm/cold state, and metric; no single run is presented as a universal guarantee.
- [ ] Logger/signpost messages exclude secrets and unnecessary personal content, and the route for viewing them (Console, Xcode, or Instruments) is documented.
- [ ] MetricKit evidence is labeled as real-device, system-scheduled aggregate/diagnostic data and is not confused with a local benchmark.

## Release and system-surface review

- [ ] Target membership, extension bundles, capabilities, entitlements, signing, and privacy resources are inspected in the built artifact.
- [ ] Widgets, controls, App Intents, notifications, Live Activities, and other system-owned surfaces are invoked outside the main app process where applicable.
- [ ] Physical-device assistive-technology tasks are planned for VoiceOver, Voice Control, Switch Control, and Assistive Access where supported.
- [ ] Release configuration, archive validation, TestFlight/App Store Connect metadata, and production/server/account behavior are listed as separate evidence layers.
- [ ] The final claim is no broader than the strongest evidence actually collected.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [Describing data use in privacy manifests](https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests)
- [App privacy details on the App Store](https://developer.apple.com/app-store/app-privacy-details/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Logging](https://developer.apple.com/documentation/os/logging/)
- [Recording Performance Data](https://developer.apple.com/documentation/os/recording-performance-data)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [Preparing your app for distribution](https://developer.apple.com/documentation/xcode/preparing-your-app-for-distribution)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases/)
