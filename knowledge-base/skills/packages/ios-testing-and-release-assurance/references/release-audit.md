# Release and distribution audit

Use this reference after behavior testing and before claiming that a build is
ready for TestFlight, App Review, or production. Inspect the actual archive and
the exact distributed build.

## Archive identity

- scheme and archive action target;
- bundle identifier and target family;
- marketing version and build number;
- SDK, deployment target, architectures, and supported destinations;
- archive path and UUID;
- signing identity, provisioning, team, and distribution method;
- embedded app extensions, frameworks, packages, resources, and privacy
  manifests;
- `Info.plist` usage descriptions, URL schemes, associated domains, background
  modes, App Groups, capabilities, and entitlements.

Do not infer archive contents from project settings. Inspect the built artifact
and record the command/tool that produced the result.

## Release configuration

Compare Debug, test, and Release settings for values that can change behavior:

- optimization, assertions, compiler flags, and feature flags;
- server/base URL, logging/redaction, analytics, and telemetry;
- model/resource inclusion and asset download policy;
- file protection, Keychain access groups, App Groups, and migration stores;
- privacy manifest and required-reason API declarations;
- background modes, push environment, associated domains, and entitlements;
- target membership and extension host configuration.

Test with the debugger disconnected when watchdog, suspension, background
execution, or process-lifecycle behavior matters. A Development-signed build
can be useful for diagnosis but should not stand in for the intended
distribution path.

## Install/update scenarios

Run and record:

1. fresh install with clean app data;
2. update from the prior release with real migration data;
3. app launch after process termination and device restart where relevant;
4. locked/unlocked and permission denied/revoked paths;
5. offline/retry/account-change/model-unavailable paths;
6. Keychain/App Group persistence and deletion policy;
7. extension/widget/system-surface launch from the actual host;
8. accessibility task on the signed build if the claim is accessibility-related.

The test run should name the device, OS, build, account, permissions, locale,
appearance, and any accessory/system host. Keep raw personal data out of the
packet; retain sanitized identifiers and result state.

## TestFlight handoff

- confirm the uploaded build number matches the inspected archive;
- record processing status and the internal/external tester path;
- install the exact TestFlight build on the named physical device;
- repeat the critical task and recovery path;
- record crashes, hangs, missing entitlements, missing resources, permission
  copy, model readiness, and system-surface behavior;
- separate a TestFlight observation from App Review acceptance and production
  rollout.

## Release claim wording

Use precise wording:

| Avoid | Use |
| --- | --- |
| “The app is Apple-approved.” | “The named build passed our source/build/device/TestFlight gates; App Review status is unverified.” |
| “Works on iPhone.” | “The critical task completed on device model/OS/build with the listed settings.” |
| “Accessible.” | “The automated audit found no listed issues on these screens, and the named VoiceOver task passed on this device.” |
| “Private AI.” | “This run used the named on-device/model route with the listed input, retention, and fallback policy.” |
| “Release ready.” | “The archive and TestFlight gates passed; the remaining App Review/production gaps are listed.” |

## Evidence record

```text
archive:
archive_uuid:
scheme/configuration:
bundle_ids_and_versions:
sdk/deployment/targets:
signing/entitlements/privacy:
extensions/resources:
device/OS/settings/account:
fresh_install_result:
update_migration_result:
TestFlight_build:
critical_task:
observed_result:
open_gaps:
```

## Sources

- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)
- [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
