# Xcode archive, signing, TestFlight, and App Store release

## Purpose

An app is not release-ready because the SwiftUI screen is polished or the
Debug build runs on a simulator. The release route joins the project’s target
graph, build configuration, bundle identity, signing, entitlements, privacy
resources, archive contents, device run, TestFlight processing, App Store
metadata, and production rollout.

Use this page with:

- [Release-ready native design and privacy](../21-design-deep-dives/103-release-ready-native-design-and-privacy.md)
- [Xcode archive, signing, and TestFlight capability route](../50-capability-recipes/106-xcode-archive-signing-testflight-route.md)
- [Xcode archive, signing, and TestFlight proof matrix](../60-verification/100-xcode-archive-signing-testflight-proof-matrix.md)
- [Xcode archive, signing, and TestFlight recipes](../70-code-recipes/118-xcode-archive-signing-testflight-recipes.md)

## Release is a chain of identities

Treat every release as a tuple, not a screenshot:

    source revision
      -> project/scheme
      -> target graph and bundle IDs
      -> version and build strings
      -> build configuration
      -> archive
      -> signed artifact and entitlements
      -> App Store Connect processed build
      -> TestFlight or App Review selection
      -> rollout and observed production build

| Identity | Why it matters | Evidence |
| --- | --- | --- |
| Source revision | Explains what was built | Commit/tag or immutable source snapshot |
| Xcode/project | Defines targets, schemes, settings, resources | Project inspection and selected toolchain |
| App target | Owns the shipped application bundle | Target membership and bundle identifier |
| Extension targets | Run in separate processes and may have separate entitlements | Widget/App Intent/notification/provider target inspection |
| Version string | Associates the build with an App Store version | Bundle and App Store Connect record |
| Build string | Uniquely identifies an upload for that version | Bundle, archive, upload record |
| Signing identity/profile | Grants the selected artifact its distribution authority | Signed bundle/provisioning inspection |
| Entitlements | Authorize capabilities and system surfaces | Signed entitlements, not just project checkboxes |
| Privacy resources | Describe data and required-reason API use | Bundled privacy manifests and privacy report |
| Processed build | Apple accepted and indexed the upload for the app record | App Store Connect build status |
| Release state | Describes beta, review, availability, and rollout | TestFlight/App Store Connect status and user-like run |

When one tuple member changes, repeat the relevant proof. A project setting is
not necessarily the same as the value in the signed bundle.

## Build configuration: Debug is not Release

Xcode normally maps the Run action to Debug and the Archive action to Release,
but projects can customize this relationship. Inspect the active scheme and
target build settings before a release run.

Release differences can include:

- optimization and compiler behavior;
- assertions and logging;
- watchdog and debugger timing;
- symbol generation and dSYM handling;
- API keys, service URLs, feature flags, and privacy configuration;
- resource processing and asset thinning;
- code signing and entitlements;
- local model, shader, package, and extension membership;
- store/account environment.

A Release build may expose a data race, watchdog issue, missing resource,
different migration path, or unavailable fallback that a Debug run hides. Test
the archive or a Release install in a user-like environment. Keep any
development-only diagnostic path visibly separate from the product path.

## Archive creation and Organizer

To create an archive, choose the scheme and a run destination appropriate for
the product, then choose the Archive action. The archive contains the app build
and debugging information and is retained by Xcode’s Organizer for later
validation or distribution.

An archive is a snapshot of configuration and signing, not proof of App Store
processing or production behavior. After archiving:

1. inspect the archive’s products and embedded targets;
2. inspect bundle IDs, version/build, architectures, resources, privacy files,
   entitlements, and linked frameworks;
3. run limited validation in Xcode;
4. install and exercise the Release artifact on the named physical device;
5. distribute through the intended channel only after the route passes;
6. retain the archive, dSYM, result bundle, validation log, and distribution
   record.

Use App Thinning options and supported device variants deliberately. A single
device run does not prove every sliced artifact or device family.

## Signing, profiles, and entitlements

Code signing answers which team and distribution identity produced the bundle.
Provisioning and entitlements answer which capabilities the signed artifact may
use. Keep these concerns explicit:

| Concern | Check |
| --- | --- |
| Team | Correct development team for the target and distribution account |
| Bundle ID | Exact App ID/target identity for app and each extension |
| Certificate | Distribution identity is current and intended |
| Provisioning | Profile matches the bundle, team, device/distribution channel, and capabilities |
| Entitlements | Signed artifact contains the required capability values |
| App Groups | Shared container identifiers match every participating target |
| Associated Domains | Signed services match the public domain configuration |
| iCloud/CloudKit | Container identifiers and environment match the release |
| Health/Home/Network/etc. | Capability approval, usage strings, and target membership are aligned |
| Push | APS environment/topic/provider configuration matches the build |

Do not print, commit, or put signing private material, App Store Connect API
keys, certificates, provisioning profiles, JWTs, or server credentials in the
knowledge base or an app bundle. Pass opaque credentials through approved
secret storage and record only safe key IDs, environment names, or redacted
fingerprints.

Project capabilities are intent. Inspect the signed app and extension
entitlements to know what the artifact actually carries.

## Target and resource inspection

The release target graph should answer:

- Which app target is archived?
- Which widget, control, Live Activity, App Intent, notification, Share,
  document, Watch, App Clip, or provider targets are included?
- Which resources are copied into which bundle?
- Which Swift packages/products are linked by each target?
- Which privacy manifests and localization resources are present?
- Which Info.plist usage strings and URL schemes are in the signed product?
- Which deployment targets and architectures were selected?
- Which capabilities are app-only versus extension-required?

Do not infer extension behavior from the main app target. An extension can have
different lifecycle, memory, host, entitlements, privacy, and system timing.

For on-device AI, inspect model and resource membership, but also record model
readiness and device support separately. A bundled model file or Foundation
Models import does not prove that the selected device can run the intended
profile.

For Liquid Glass, inspect that the app uses the current SDK route and that
custom effects are app-owned functional surfaces. Do not attempt to package a
copy of a system-owned control, widget, notification, or Apple Intelligence
surface.

## Version and build identity

App Store Connect uses the bundle ID and version number from the uploaded app
bundle to associate it with an app/version record. The build string uniquely
identifies the upload through the system.

Choose a policy before upload:

- version changes for a new App Store version;
- build increments for every upload of that version;
- extensions and embedded products agree with the app’s compatibility policy;
- migration and rollback can identify the exact previous build;
- screenshots, support notes, crash logs, and TestFlight feedback include the
  build identity.

Never overwrite a build string and assume App Store Connect will treat it as a
new artifact. When a new build is needed, increment according to the project’s
policy and record why.

## Privacy manifests and required-reason APIs

A privacy manifest is a bundled property-list resource named
PrivacyInfo.xcprivacy. It describes app or third-party SDK data collection and
required-reason API use. SDKs delivered as XCFrameworks, Swift packages, or
Xcode projects can have their own manifests.

Verify:

1. the manifest is valid and uses expected keys/values;
2. it is a resource of the intended target;
3. each app or SDK that uses a covered required-reason API reports the correct
   category and approved reason;
4. collected data, tracking domains, and tracking declaration match the actual
   product behavior;
5. third-party SDK manifests are present and not assumed to be covered by the
   app’s manifest;
6. the archive and generated privacy report contain the expected records;
7. App Store Connect App Privacy answers agree with the app and SDK behavior.

An empty or copied manifest is not compliance. The reason must accurately match
the code path and declared product functionality. Privacy review is a
source/configuration/artifact/behavior comparison, not a checkbox.

## TestFlight is a distinct distribution environment

Upload a processed build to App Store Connect before assigning it to TestFlight.
Processing status, export compliance, tester group, test information, and build
availability are separate steps.

TestFlight evidence should record:

- exact build string and processing status;
- internal or external tester group;
- whether external testing review is required;
- tester device/OS and account state;
- install and update path;
- permissions, login, server, model, and system-surface environment;
- feedback and crash/log context tied to the build;
- expiration or beta-window assumptions.

TestFlight can reveal release-only behavior, but it is not the App Store, not
App Review approval, and not proof that every production service or device works.
Do not claim production from a tester install.

## App Store Connect and App Review

Before submission, the App Store Connect app record and version need the
required metadata and the intended processed build. Choose the build carefully;
the association is reversible before submission but should be recorded in the
release packet.

Review the product as a person will receive it:

- app name, description, keywords, category, age rating, and privacy answers;
- screenshots, previews, accessibility information, and localization;
- login/demo account and reviewer notes when needed;
- subscription, StoreKit, Game Center, App Clip, background asset, and
  system-surface metadata;
- export compliance and encryption documentation where applicable;
- support/contact/privacy-policy URLs;
- release option: manual, automatic, or phased availability;
- server, push, account, and remote configuration state.

App Review guidelines are a policy boundary. A working build can still be
rejected or delayed for metadata, privacy, safety, content, account access,
payment, or incomplete reviewer instructions.

## Release gate for on-device AI

Before distribution, record:

- which APIs and OS/device availability checks are used;
- model/profile/prompt/schema versions;
- model asset or system-model readiness behavior;
- no-model, refusal, context-limit, timeout, and cancellation fallbacks;
- evaluation dataset and quality criteria version;
- privacy/retention policy for source inputs and generated output;
- review and confirmation path for side effects;
- Release/TestFlight performance and battery observations;
- archive membership of AI resources and privacy manifests.

Do not make a model quality claim from one device or one prompt. Do not let a
generated proposal bypass the same validation and revision checks used by a
human edit.

## Release gate for Liquid Glass and native design

Exercise the signed Release/TestFlight build with:

- light/dark appearance and increased contrast;
- large Dynamic Type and long/localized labels;
- reduced motion and reduced transparency/effects;
- VoiceOver, Voice Control, Switch Control, keyboard/pointer where supported;
- empty, loading, stale, offline, error, and disabled states;
- rotation/size class and supported device family;
- cold launch, resumed launch, deep-link/system entry, and process termination;
- scroll/animation/hitch observations on a representative physical device.

The effect is not the product. The content hierarchy, semantic action, privacy
state, and system behavior are the release surface.

## What each artifact can prove

| Artifact | Can prove | Cannot prove |
| --- | --- | --- |
| Source/README | Intended route and policy | Build or behavior |
| Project target | Declared graph/settings | Signed output |
| Archive | Captured build and selected distribution configuration | App Store processing or production |
| Validate App | Limited automated validation feedback | Full device/system/review behavior |
| Signed device run | Artifact runs on that device and environment | All devices, review, production |
| TestFlight build | Processed beta distribution and tester path | App Store availability or universal quality |
| App Store submission | Metadata/build entered review workflow | Approval or live health |
| Production observation | Defined field behavior for a build/population | Universal guarantee |

## Sources

- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Build settings reference](https://developer.apple.com/documentation/xcode/build-settings-reference)
- [Swift packages in Xcode](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
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
