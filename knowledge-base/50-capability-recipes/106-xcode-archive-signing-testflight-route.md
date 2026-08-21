# Xcode archive, signing, TestFlight, and App Store release route

## Use this route when

Use this route when an iOS app, extension, App Clip, Watch companion, widget,
Control, Live Activity, App Intent, or on-device AI feature must leave the local
Debug environment.

Read the [archive/signing deep dive](../42-framework-deep-dives/75-xcode-archive-signing-testflight-and-release.md),
the [release-ready design contract](../21-design-deep-dives/103-release-ready-native-design-and-privacy.md),
the [proof matrix](../60-verification/100-xcode-archive-signing-testflight-proof-matrix.md),
and the [recipes](../70-code-recipes/118-xcode-archive-signing-testflight-recipes.md).

## Route contract

    source/tag
      -> project and scheme audit
      -> Release configuration
      -> target/resource/privacy audit
      -> archive
      -> signed artifact inspection
      -> Validate App
      -> physical Release run
      -> App Store Connect upload and processing
      -> TestFlight
      -> App Store metadata/build selection
      -> App Review
      -> rollout and monitoring

Each arrow is a gate. Do not skip from a green local build to a production
claim.

## Step 1: freeze the release input

Create a release record before changing the project:

| Field | Record |
| --- | --- |
| Source revision | Commit/tag or immutable source reference |
| Xcode/SDK | Selected Xcode and SDK version |
| Deployment | Minimum iOS and supported device families |
| Scheme | Exact archive scheme |
| Configuration | Release configuration and any custom settings |
| App version | Version string |
| Build | Unique build string |
| Team | Distribution team identifier, not a secret |
| Environment | Production-like/sandbox/staging name |
| AI profile | Model/profile/prompt/schema version or none |
| Feature flags | Safe names and values, never secrets |

If the build identity changes, invalidate the old release packet or mark it
superseded.

## Step 2: audit the target graph

List every target that must ship or be invoked:

- application;
- widgets and Control extensions;
- Live Activity/activity extension;
- App Intent or App Intents extension;
- notification content/service;
- Share/File Provider/document provider;
- App Clip;
- Watch app/extension;
- CarPlay scene;
- custom extension or provider;
- package products, resources, macros, plugins, and AI model assets.

For each target, record bundle ID, deployment, host, resources, entitlements,
privacy manifest, signing, and system configuration. Do not use the main app’s
successful run as evidence for an extension.

## Step 3: align version/build and resources

Confirm that:

1. app bundle ID matches the App Store Connect app record;
2. version string matches the intended App Store version;
3. build string is new for the upload and aligned with the update policy;
4. embedded targets use compatible identity and build settings;
5. localizations, app icons, launch assets, model files, shader libraries,
   privacy manifests, and package resources are in the intended bundle;
6. the archive contains no development-only secrets or endpoints.

Use archive inspection to verify the output rather than trusting the project
navigator.

## Step 4: configure signing and capabilities

Use the team’s approved signing workflow. Inspect:

- distribution certificate/identity;
- provisioning profile;
- App ID and bundle IDs;
- entitlements in the signed artifact;
- App Groups and shared containers;
- associated domains;
- iCloud/CloudKit;
- push environment;
- Health/Home/Network/Background/Family Controls or other protected
  capabilities;
- extension host and system approval.

Do not place private signing material or App Store Connect API credentials in
the source tree, build logs, app bundle, or screenshots.

## Step 5: validate privacy

For the app and each relevant SDK/target:

- locate PrivacyInfo.xcprivacy;
- validate expected keys/values;
- declare required-reason APIs accurately;
- reconcile collected data and tracking domains with behavior;
- inspect third-party SDK manifests;
- include the file in target resources;
- compare archive/privacy report/App Store Connect answers;
- update the privacy policy and user-facing explanation when behavior changed.

Treat invalid or missing manifests as a release blocker when the route requires
them. Do not copy a generic manifest to silence a validation warning.

## Step 6: build and inspect the archive

Choose the intended scheme and archive destination. Produce the Release archive
and retain:

- archive path;
- dSYM and symbol information;
- build log;
- validation result;
- signed entitlements;
- bundle/resource inventory;
- privacy manifest/report;
- version/build identity;
- target list and architectures.

Run Xcode’s limited validation. Resolve warnings that affect the selected route,
but distinguish an automated validation result from a device, system, review, or
production result.

## Step 7: run the signed Release artifact

Install the Release artifact on a representative physical device. Exercise:

- clean install and update;
- permission grant/deny/revoke;
- account sign-in/out and expired state;
- offline/slow network;
- model unavailable/refusal/timeout;
- AI review and commit/reject;
- Liquid Glass adaptation and reduced effects;
- VoiceOver/Dynamic Type/reduced motion;
- extensions/system surfaces;
- background/termination/resume;
- migration and rollback-safe data behavior.

Record device, OS, build, configuration, account, network, model/profile, and
result. A development-signed Release build may not expose every distribution
behavior; TestFlight remains a separate gate.

## Step 8: upload and wait for processing

App Store Connect associates an upload from the bundle ID and version, with the
build string identifying the build. Upload with Xcode, Transporter, or an
approved automation route. Keep credentials out of scripts and logs.

After upload:

1. retain the delivery identifier/log;
2. wait for processing;
3. inspect warnings/errors and build status;
4. verify variants and metadata;
5. confirm the processed build matches the release record;
6. do not select a build that was not inspected.

An upload request or local archive does not prove the processed build is
available.

## Step 9: TestFlight

Create a tester plan:

| Group | Use |
| --- | --- |
| Internal | Fast checks by App Store Connect users with access |
| External | Broader beta; may require App Review for the build/group |
| Device matrix | Supported iPhone/iPad/OS combinations actually tested |
| Scenario matrix | Onboarding, update, permissions, AI, system surface, offline |
| Feedback | Build-linked, privacy-safe diagnostic path |

Test the install/update path, app expiration assumptions, account/server state,
push/system surfaces, and device performance. TestFlight feedback is beta
evidence, not App Store production evidence.

## Step 10: prepare submission

Before App Review:

- create/verify the App Store version record;
- enter required metadata and localizations;
- choose the processed build;
- verify screenshots/previews and accessibility information;
- provide reviewer notes/demo account/hardware instructions when needed;
- complete privacy, age rating, export compliance, encryption, and pricing data;
- confirm StoreKit, Game Center, App Clip, background asset, and other linked
  items are in the intended submission;
- choose manual, automatic, or phased release;
- preserve the exact submission record.

A build can be technically valid and still not be ready for review if the
metadata, access path, privacy answer, or reviewer information is incomplete.

## Step 11: release and monitor

After approval, record:

- release option and time;
- version/build;
- availability regions;
- initial install/update;
- production server/push/account/model state;
- crash, performance, and AI-quality monitoring;
- rollback or kill-switch policy;
- support path and App Review communication.

Production behavior is a new evidence layer. Do not claim that a TestFlight
build’s behavior applies to every production device or region.

## Failure states

| Failure | Response |
| --- | --- |
| Wrong bundle ID/version | Stop; do not upload or select the build |
| Duplicate build string | Increment through the release policy |
| Missing extension | Fix target membership and re-archive |
| Missing entitlement | Fix capability/approval/signing, then inspect signed output |
| Invalid privacy manifest | Correct the manifest/SDK and revalidate |
| Build processing error | Inspect the processed upload and delivery log |
| TestFlight build unavailable | Wait for processing or correct App Store metadata |
| External beta review required | Treat review as a separate gate |
| AI/model unavailable | Ship fallback or defer the gated feature |
| Liquid Glass inaccessible | Fix semantic hierarchy/adaptation before distribution |
| App Review issue | Address the policy/metadata/product issue; do not bypass it |

## Output packet

The route produces:

- release record;
- target graph and archive inventory;
- signed entitlements/profile evidence;
- privacy manifest/report and App Store privacy reconciliation;
- Release physical-device run;
- upload/processing log;
- TestFlight build/tester record;
- App Store version/build selection;
- submission/review state;
- rollout/monitoring plan;
- known gaps.

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
