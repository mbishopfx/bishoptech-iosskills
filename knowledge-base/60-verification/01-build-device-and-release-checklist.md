# Build, Device, and Release Checklist

## Before building

- [ ] Target SDK and deployment target are recorded.
- [ ] Required frameworks, capabilities, entitlements, and privacy descriptions are listed.
- [ ] The source registry was refreshed for new APIs.
- [ ] The app has a deterministic fallback for unavailable device services.
- [ ] Test data is synthetic or appropriately redacted.

## Privacy resources and target configuration

- [ ] Every app, framework, static/dynamic SDK, widget, and extension target has an explicit privacy-manifest ownership decision.
- [ ] `PrivacyInfo.xcprivacy` is target-owned, included in the expected bundle resources, valid, and checked for the exact `NSPrivacy*` keys and approved values used.
- [ ] Required-reason API categories are traced through app code and third-party SDKs; an SDK’s own manifest is not replaced by the app manifest.
- [ ] App Store Connect App Privacy answers, privacy-policy URL, and user-facing permission copy match the actual data flow, retention, tracking, and remote-processing behavior.
- [ ] The final archive privacy report is generated and reviewed before distribution.

## Build and test

- [ ] Build the exact scheme and configuration used for the target.
- [ ] Run unit tests for domain rules, persistence, authorization mapping, and fallback states.
- [ ] Run UI tests or deterministic scenario tests for core routes.
- [ ] Inspect the test result bundle rather than relying only on process exit text.
- [ ] Check warnings, signing, embedded extensions, and app/extension bundle identifiers.
- [ ] Record the active `.xctestplan`, test configurations, tags, destinations, and test command.
- [ ] Run a focused development plan and a broader pre-submission plan when the project has both; confirm skipped/excluded tests are intentional.
- [ ] Add performance tests for critical paths and record baselines with the device, OS, build, workload, and warm/cold state.
- [ ] Use `Logger` and `OSSignposter` for diagnosable operations without logging secrets or unnecessary user content.

## Simulator

- [ ] Test empty/loading/success/error states.
- [ ] Test navigation from cold launch and deep link.
- [ ] Test light/dark, Dynamic Type, increased contrast, Reduce Motion, and Reduce Transparency.
- [ ] Test permission-denied and unavailable branches with mocked services where hardware is absent.
- [ ] Label simulator evidence as simulator evidence.

## Physical device

- [ ] Verify the intended device family and iOS version.
- [ ] Verify camera, microphone, location, motion, Bluetooth, NFC, haptics, Apple Intelligence, and background behavior on actual hardware when used.
- [ ] Verify the built app’s entitlements and Info.plist values.
- [ ] Test lock/unlock, interruption, termination, relaunch, and settings changes.
- [ ] Capture evidence with the device, build, OS, and scenario identified.
- [ ] Test VoiceOver, Voice Control, Switch Control, Assistive Access, Dynamic Type, reduced motion/transparency, and alternate input on supported physical devices where they affect the feature.
- [ ] Test MetricKit integration on physical hardware; label debug-simulated payloads separately from real-device reports.

## Distribution

- [ ] Test StoreKit sandbox or TestFlight behavior where relevant.
- [ ] Test privacy disclosures and permission copy in the distributed build.
- [ ] Test app links, widgets, extensions, and App Intents in the signed artifact.
- [ ] Review App Store metadata and claims against shipped behavior.
- [ ] Do not call the app release-ready until all required gates have evidence.
- [ ] Archive with the intended Release configuration, validate the archive, and inspect bundle identifiers, version/build, entitlements, embedded extensions, symbols, and privacy resources.
- [ ] Treat TestFlight as beta distribution/testing evidence and the App Store submission/release state as a separate gate.
- [ ] Record server, APNs, account, storefront, capability, and environment state for any route whose behavior depends on external services.

## Sources

- [Xcode documentation](https://developer.apple.com/documentation/xcode)
- [Testing](https://developer.apple.com/documentation/testing)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [Describing data use in privacy manifests](https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Adding tests to your Xcode project](https://developer.apple.com/documentation/xcode/adding-tests-to-your-xcode-project)
- [Improving code assessment by organizing tests into test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
- [Running tests and interpreting results](https://developer.apple.com/documentation/xcode/running-tests-and-interpreting-results)
- [Logging](https://developer.apple.com/documentation/os/logging/)
- [Recording Performance Data](https://developer.apple.com/documentation/os/recording-performance-data)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [MXMetricManager](https://developer.apple.com/documentation/metrickit/mxmetricmanager)
- [MetricKit updates](https://developer.apple.com/documentation/updates/metrickit)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [VoiceOver](https://developer.apple.com/documentation/accessibility/voiceover)
- [Optimizing your app for Assistive Access](https://developer.apple.com/documentation/accessibility/optimizing-your-app-for-assistive-access)
- [Preparing your app for distribution](https://developer.apple.com/documentation/xcode/preparing-your-app-for-distribution)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases/)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)
- [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds)
