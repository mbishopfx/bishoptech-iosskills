# Xcode archive, signing, TestFlight, and release proof matrix

## Purpose

This matrix records the evidence needed to move an iOS app from source to a
signed, processed, testable, and submit-ready artifact. It is used with the
[release deep dive](../42-framework-deep-dives/75-xcode-archive-signing-testflight-and-release.md),
the [release-ready design contract](../21-design-deep-dives/103-release-ready-native-design-and-privacy.md),
the [capability route](../50-capability-recipes/106-xcode-archive-signing-testflight-route.md),
and the [release recipes](../70-code-recipes/118-xcode-archive-signing-testflight-recipes.md).

## Evidence levels

| Level | Artifact | Supports | Does not support |
| --- | --- | --- | --- |
| R0 | Source/configuration contract | Intended target, privacy, capability, and release policy | Built behavior |
| R1 | Named target compile | Imports, target graph, resource references, availability | Signed artifact or device behavior |
| R2 | Archive | Release configuration snapshot, products, debugging symbols | Apple processing, TestFlight, review, production |
| R3 | Archive inspection and limited validation | Bundle identity, target/resource/privacy/signing consistency, validation feedback | Full runtime/system/review behavior |
| R4 | Signed physical Release run | User-like artifact on a named device/OS | All device families, App Store processing, universal performance |
| R5 | Processed TestFlight build | Apple-hosted beta install/update/tester path | App Store availability or App Review approval |
| R6 | App Store submission | Required metadata/build entered review workflow | Approval, rollout, or production health |
| R7 | Production observation | Defined build/population behavior and monitoring | Universal guarantee |

## Release identity matrix

| Item | Evidence to capture | Failure if missing |
| --- | --- | --- |
| Source revision | Commit/tag and dirty-state policy | Cannot reproduce artifact |
| Xcode/SDK | Toolchain version and platform SDK | Version-sensitive mismatch |
| Scheme | Archive scheme and destination | Wrong target graph |
| Configuration | Release settings and overrides | Debug behavior mistaken for Release |
| Bundle ID | Archive bundle and App Store record | Upload cannot associate correctly |
| Version | Bundle/App Store version | Wrong app version |
| Build | Bundle/archive/upload build string | Duplicate or wrong build selection |
| Targets | App and every extension/product | Missing system surface |
| Resources | Icons, localizations, models, shaders, privacy | Runtime missing asset |
| Signing | Team/certificate/profile identity | Distribution/install failure |
| Entitlements | Signed bundle values | Capability absent or unauthorized |
| Privacy | Manifest/report/App Store answers | Invalid/inconsistent privacy declaration |
| Archive | Retained archive/dSYM/log | Cannot inspect or reproduce |
| Processed build | App Store Connect status | Upload not usable |

## Target and artifact matrix

| Target | Inspect | Runtime/system proof |
| --- | --- | --- |
| Main app | Bundle ID, version/build, resources, privacy, entitlements | Signed install and primary tasks |
| Widget | Extension bundle, widget families, shared projection, privacy | Widget host on physical device |
| Control | Control configuration, App Intent, locked state, target | Control Center/Lock Screen host |
| Live Activity | Activity target, attributes/content, push/local configuration | Lock Screen/Dynamic Island host |
| App Intent | Intent target/package, parameters, auth, result | Siri/Shortcuts/Spotlight/system invocation |
| Notification service/content | Extension point, entitlements, payload behavior | Remote/local notification host |
| App Clip | Clip bundle, associated domain/experience, size | Physical invocation and full-app handoff |
| Watch | Watch targets, transfer resources, pairing | Paired iPhone/Watch run |
| CarPlay | Scene/category/entitlement | Supported vehicle/CarPlay environment |
| Share/document/provider | Extension point, UTIs, security scope | Files/Share/host invocation |
| AI/model asset | Resource/package membership, profile/readiness | Supported physical device and fallback |

A main-app compile does not close any row for a separate host or extension.

## Signing and entitlement matrix

| Capability | Project check | Signed artifact check | Runtime proof |
| --- | --- | --- | --- |
| App Groups | Group declared on targets | Entitlement contains exact identifiers | Shared data handoff |
| Associated Domains | Capability and domains | Signed services match | Physical Universal Link/Handoff |
| iCloud/CloudKit | Containers/environment | Entitlements and archive | Account/sync device run |
| Push | Background/remote configuration | APS environment/topic | Provider/device delivery |
| Health/Home/Network | Capability and usage text | Entitlement/approval | Physical authorization/service |
| Family Controls/SensorKit/etc. | Approval and target setup | Distribution entitlement | Approved signed route |
| Extension host | Extension point/Info.plist | Embedded signed target | Host invocation/relaunch |

Never store a private key, token, or profile secret in a result bundle. Record
safe identifiers and redacted fingerprints only.

## Privacy manifest matrix

| Check | Evidence | Stop condition |
| --- | --- | --- |
| File exists | PrivacyInfo.xcprivacy in expected target/resource | Missing file where required |
| Valid schema | Xcode/validation report and expected keys | Unexpected keys/values |
| Required reasons | API category and approved reason | Use not accurately described |
| SDK coverage | Third-party manifest inventory | SDK assumed covered by app manifest |
| Data collection | Runtime/source/SDK inventory | App Privacy answers disagree |
| Tracking domains | Manifest/network/privacy policy | Declared tracking mismatch |
| Archive placement | Bundle/resource inspection | File not in signed artifact |
| Submission | App Store Connect privacy answers | Metadata not reconciled |

An archive’s manifest proves contents, not that runtime collection or retention
matches the declaration. Keep behavior review separate.

## Release build test matrix

| Scenario | Device/configuration | Record |
| --- | --- | --- |
| Clean install | Physical Release device | Install, launch, version/build |
| Update | Previous production/TestFlight data | Migration, keychain, defaults, store |
| Permission grant/deny/revoke | Device settings | Prompt, fallback, recovery |
| Account switch/sign out | Test account | Redaction, cache, entitlement |
| Network loss | Physical device | Offline state, retry, no duplicate commit |
| AI model unavailable | Unsupported/not-ready path | Manual fallback and no silent side effect |
| AI review/commit | Supported device/profile | Proposal, validation, explicit acceptance |
| Liquid Glass adaptation | Appearance/accessibility settings | Legibility, focus, motion/effects |
| Extension/system surface | Host device/system | Target delivery, stale/privacy state |
| Background/termination | Device with lifecycle interruption | Checkpoint, restore, no duplicate action |
| Performance | Representative physical device | Launch/hitch/memory/thermal context |

## Upload and processing matrix

| Stage | Evidence | Does not prove |
| --- | --- | --- |
| Archive selected | Scheme/destination/archive ID | App Store processing |
| Validate App | Xcode validation result | Every device/system behavior |
| Upload | Delivery log and upload ID | Processed availability |
| Processing | App Store Connect build status | TestFlight tester path |
| Build metadata | Bundle/version/build/variants | Correct user-facing version by itself |
| TestFlight assignment | Group/build/test info | App Store approval |
| External beta review | Review status and feedback | Production release |
| Build selection | Version/build association | App Review outcome |
| Submission | Draft/Ready/In Review status | Live availability |
| Release | Manual/automatic/phased state | Field health |

## TestFlight matrix

| Test | Internal | External | Evidence |
| --- | --- | --- | --- |
| Processed build appears | Yes | Yes | Build status and version |
| Clean install | Yes | Yes | Device/OS/build |
| Update from prior build | Yes | Yes | Migration and rollback behavior |
| Permissions/account | Yes | Yes | State and recovery |
| System surface | Yes | Yes | Physical host/paired device |
| AI quality/fallback | Yes | Yes | Profile/dataset/feedback |
| Accessibility | Yes | Yes | Physical task |
| Crash/performance | Yes | Yes | Build-linked diagnostics |
| External beta review | No | Possibly | Review status |

## App Review submission matrix

| Submission item | Evidence |
| --- | --- |
| Correct app/version | App Store Connect record |
| Correct processed build | Selected build identity |
| Metadata/localization | Required fields and screenshots |
| Privacy/App Privacy | Answers reconciled with manifest/behavior |
| Accessibility | Declarations and tested tasks |
| Login/reviewer path | Demo account/instructions if needed |
| Export/encryption | Required documentation |
| StoreKit/Game Center/App Clip/assets | Associated item status |
| Release option | Manual/automatic/phased decision |
| Support/privacy URLs | Reachable current destinations |

Review workflow status is not approval, and approval is not production health.

## AI release matrix

| Claim | Required proof |
| --- | --- |
| API available | SDK/deployment and runtime availability |
| Model can run | Supported physical device/profile readiness |
| Output is reviewable | Typed proposal and UI task |
| Output is safe | Deterministic validator/policy result |
| Prompt is effective | Versioned dataset/criteria report |
| Commit is correct | Revision/idempotency/domain test |
| Fallback works | No-model/refusal/timeout Release run |
| Performance is acceptable | Physical Release workload/metric |
| Privacy is consistent | Manifest/source/runtime/metadata reconciliation |
| System projection is ready | Target/archive/host run |

## Liquid Glass release matrix

| State/setting | Proof |
| --- | --- |
| Normal ready | Physical Release interaction |
| Loading/error/offline | State fixture and UI workflow |
| Large Dynamic Type | Device task and layout |
| VoiceOver | Full task, focus, labels, actions |
| Reduced motion/effects | Device behavior and fallback |
| Increased contrast/dark mode | Legibility and hierarchy |
| Long/localized content | Device layout and UI test |
| Scroll/animation | Hitch/performance context |
| System-owned surface | Host/system invocation, not app screenshot |

## Stop conditions

Stop the release packet when:

- bundle ID/version/build is not recorded;
- the archive scheme or Release configuration is unknown;
- a target/resource/extension is assumed from source but not in the archive;
- project capability is not confirmed in signed entitlements;
- a private signing/API credential appears in artifacts or logs;
- privacy manifest/SDK/App Store answers disagree;
- upload is not processed or build selection is ambiguous;
- TestFlight feedback is not tied to a build;
- App Review metadata or reviewer path is incomplete;
- AI/model claims lack device/profile/fallback evidence;
- Liquid Glass claims lack accessibility/reduced-effects/physical proof;
- production behavior is claimed from Debug, simulator, archive, or TestFlight alone.

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
