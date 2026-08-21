# Xcode archive, signing, TestFlight, and release recipes

## How to use these sketches

These are release route sketches, not a claim that this documentation workspace
contains a shippable app. Apply them to a named project, inspect the real
archive, and keep credentials outside source and logs. Use the [release
capability route](../50-capability-recipes/106-xcode-archive-signing-testflight-route.md),
the [proof matrix](../60-verification/100-xcode-archive-signing-testflight-proof-matrix.md),
the [release design contract](../21-design-deep-dives/103-release-ready-native-design-and-privacy.md),
and the [release deep dive](../42-framework-deep-dives/75-xcode-archive-signing-testflight-and-release.md).

## Release record

Create a redacted record that is safe to keep with artifacts:

~~~yaml
source_revision: record-commit-or-tag
xcode: record-selected-version
sdk: record-selected-ios-sdk
deployment_target: record-minimum-ios
scheme: ExampleApp
configuration: Release
version: 1.0.0
build: 42
team: redacted-team-id
environment: production-like
ai_profile: record-profile-or-none
feature_flags:
  - local-ai-review
archive: artifacts/ExampleApp.xcarchive
validation: artifacts/validation-log.txt
result_bundle: artifacts/release-tests.xcresult
known_gaps:
  - production-push-not-tested
~~~

Replace every placeholder. Do not put certificate private keys, provisioning
profile secrets, App Store Connect API keys, JWTs, or account tokens in this
record.

## Archive with xcodebuild

Use explicit project, scheme, configuration, destination, and archive path:

~~~sh
xcodebuild \
  -project ExampleApp.xcodeproj \
  -scheme ExampleApp \
  -configuration Release \
  -destination "generic/platform=iOS" \
  -archivePath artifacts/ExampleApp.xcarchive \
  archive
~~~

For a workspace, use workspace and scheme instead of project. The exact
destination and signing settings are project-specific. Capture the command,
toolchain, exit status, build log, and archive path.

An archive command succeeding proves that Xcode produced an archive for the
selected scheme/configuration. It does not prove that the artifact has the
right entitlements, App Store metadata, physical behavior, or production
service configuration.

## Inspect archive products

Use filesystem inspection and Xcode Organizer to inventory the output:

~~~sh
find artifacts/ExampleApp.xcarchive/Products -maxdepth 4 -type f | sort
find artifacts/ExampleApp.xcarchive/dSYMs -maxdepth 2 -type f | sort
plutil -p artifacts/ExampleApp.xcarchive/Info.plist
~~~

For an app bundle, inspect the embedded product:

~~~sh
APP="artifacts/ExampleApp.xcarchive/Products/Applications/ExampleApp.app"
plutil -p "$APP/Info.plist"
find "$APP" -maxdepth 3 -name "PrivacyInfo.xcprivacy" -o -name "*.appex"
codesign -d --entitlements :- "$APP"
codesign --display --verbose=4 "$APP"
~~~

The shell variable is a local path placeholder. Use an explicit validated path
in a real release script and redact signing details from logs. Inspect each
embedded extension separately.

## Inspect target and bundle identity

Record the exact values that App Store Connect will use:

~~~sh
plutil -extract CFBundleIdentifier raw "$APP/Info.plist"
plutil -extract CFBundleShortVersionString raw "$APP/Info.plist"
plutil -extract CFBundleVersion raw "$APP/Info.plist"
find "$APP/PlugIns" -maxdepth 2 -name "Info.plist" -print
~~~

Compare the values with the App Store Connect app record and the release
record. A build string that was already uploaded for the same version is not a
new artifact merely because the source changed.

## Inspect privacy manifests

Inventory app and embedded SDK manifests:

~~~sh
find "$APP" -name "PrivacyInfo.xcprivacy" -print
plutil -lint "$APP/PrivacyInfo.xcprivacy"
plutil -p "$APP/PrivacyInfo.xcprivacy"
~~~

Run the same inspection for embedded frameworks and extensions when they ship
their own manifests. Compare the result with the source inventory, runtime
collection, required-reason API use, privacy policy, and App Store Connect App
Privacy answers.

## Signed entitlements checklist

Capture a redacted entitlement report:

~~~sh
codesign -d --entitlements :- "$APP" > artifacts/app-entitlements.plist
plutil -lint artifacts/app-entitlements.plist
~~~

Check the exact values for App Groups, Associated Domains, iCloud containers,
push environment, Health/Home/Network/Family Controls or other protected
capabilities, and each extension. Do not treat the project capability editor as
the final authority.

## Validate the archive

Xcode Organizer provides Validate App for limited automated validation. Keep
validation separate from distribution:

~~~sh
xcodebuild -version
xcodebuild -list -project ExampleApp.xcodeproj
~~~

Use Xcode Organizer or the selected distribution workflow to validate the
archive. Save warnings/errors and the exact archive identity. Do not automate
around a validation error without understanding whether it is target,
signing, privacy, resource, metadata, or distribution state.

## Export a device-testable build

Use Xcode’s Organizer distribution workflow or a project-approved export
configuration. Keep export options and signing decisions in the release
record, not hidden in a personal machine setting.

~~~sh
xcodebuild \
  -exportArchive \
  -archivePath artifacts/ExampleApp.xcarchive \
  -exportPath artifacts/export \
  -exportOptionsPlist Config/ExportOptions.plist
~~~

Inspect ExportOptions.plist before use. Never commit a profile UUID or
certificate private material just to make a local export repeatable.

## Run a Release test plan

Use an explicit plan and result bundle:

~~~sh
xcodebuild \
  -scheme ExampleApp \
  -configuration Release \
  -destination "platform=iOS Simulator,name=iPhone 17" \
  -testPlan ReleaseCandidate \
  test \
  -resultBundlePath artifacts/release-tests.xcresult
~~~

Replace the destination with the named supported device or simulator in the
project. Use a physical device for claims about camera, haptics, model
readiness, performance, accessibility, system surfaces, or distribution.

## TestFlight upload boundary

Upload through Xcode Organizer, Transporter, or the approved App Store Connect
automation path. Keep the upload log:

~~~yaml
archive: artifacts/ExampleApp.xcarchive
upload_method: Xcode-Organizer
upload_time: record-time
delivery_id: redacted-delivery-id
bundle_id: com.example.ExampleApp
version: 1.0.0
build: 42
processing_status: record-status
testflight_group: internal-or-external-group
external_review: required-or-not-required
~~~

Do not mark processing complete from a successful upload command. Confirm the
build appears in App Store Connect with the expected metadata and status.

## TestFlight tester matrix

~~~yaml
build: 42
groups:
  internal:
    - clean-install
    - update-from-previous
    - permission-deny-recovery
    - ai-fallback
  external:
    - primary-user-task
    - accessibility-task
    - device-matrix
    - system-surface
feedback:
  include_build_and_device: true
  redact_private_input: true
  correlation_id: support-safe-only
~~~

Testers need a meaningful task and a safe feedback channel. A tester’s
successful install does not prove App Review approval or App Store rollout.

## App Store version/build selection

Before submission, verify the processed build:

~~~yaml
app_record: ExampleApp
platform: iOS
version_record: 1.0.0
processed_build: 42
bundle_id: com.example.ExampleApp
metadata_complete: true
privacy_reconciled: true
export_compliance: complete-or-not-applicable
review_notes: present-if-needed
release_option: manual-or-automatic-or-phased
selected_by: authorized-role
selected_at: record-time
~~~

Choose the build that was actually tested. App Store Connect can contain more
than one build for a version; the selected build is part of the submission
evidence.

## Release-ready UI smoke task

Use a physical Release/TestFlight build for this sequence:

~~~text
1. Install or update the selected build.
2. Confirm version/build in the app’s safe diagnostic surface.
3. Run the primary task from empty state.
4. Deny one relevant permission and verify the fallback.
5. Enable large text and VoiceOver for the critical path.
6. Enable reduced motion/effects and verify the Liquid Glass fallback.
7. Exercise offline or service-unavailable state.
8. If AI exists, test unavailable, refusal, review, accept, reject, and stale.
9. Relaunch after termination and verify durable state.
10. Record device, OS, account, network, model/profile, and result.
~~~

This is a task record, not a universal compatibility test.

## AI release gate

Keep AI-specific evidence in a separate record:

~~~yaml
feature: review-assistant
api: Foundation-Models-or-Core-ML
os_check: recorded
device_profile: recorded
prompt_version: prompt-v3
schema_version: proposal-v2
dataset: eval-v4
deterministic_checks:
  - schema
  - source-revision
  - forbidden-side-effect
quality_criteria:
  - field-accuracy
  - omission-rate
  - human-review-utility
fallback:
  model_unavailable: manual-editor
  refusal: explain-and-continue
commit: explicit-user-action-and-domain-revision-check
release_result: record-result
~~~

Do not ship an auto-commit route simply because the local fixture produces
clean output. The Release/TestFlight build should use the same proposal,
validation, review, and commit boundaries.

## Liquid Glass and privacy smoke gate

For the signed artifact, record:

~~~yaml
appearance:
  light: pass-or-fail
  dark: pass-or-fail
adaptation:
  large_dynamic_type: pass-or-fail
  increased_contrast: pass-or-fail
  reduced_motion: pass-or-fail
  reduced_effects: pass-or-fail
accessibility:
  voiceover_primary_task: pass-or-fail
  focus_after_sheet: pass-or-fail
privacy:
  usage_copy: pass-or-fail
  manifest: pass-or-fail
  app_store_answers: pass-or-fail
  runtime_behavior: pass-or-fail
performance:
  scroll_hitch_context: record-or-not-run
  memory_thermal_context: record-or-not-run
~~~

The visual effect is one row among semantic, privacy, accessibility, and
performance rows.

## Release packet checklist

~~~text
[ ] Source revision and toolchain recorded.
[ ] Scheme, target graph, version, and build recorded.
[ ] Release archive retained.
[ ] dSYM and build logs retained.
[ ] Bundle IDs/resources/extensions inspected.
[ ] Signed entitlements inspected.
[ ] Privacy manifests validated and reconciled.
[ ] Validate App result retained.
[ ] Physical Release smoke task complete.
[ ] Upload and processing status recorded.
[ ] TestFlight build/group/feedback record complete.
[ ] App Store metadata, privacy, export, and review notes complete.
[ ] Correct processed build selected.
[ ] Rollout/monitoring/rollback plan recorded.
[ ] Known gaps remain visible.
~~~

## Sources

- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)
- [Choose a build to submit](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit)
- [Submit an app](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/)
- [Overview of publishing your app on the App Store](https://developer.apple.com/help/app-store-connect/manage-your-apps-availability/overview-of-publishing-your-app-on-the-app-store/)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
