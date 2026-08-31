---
name: meta-dat-ios-integration
description: Integrate the current Meta Wearables Device Access Toolkit into a native iOS companion app with source-checked package setup, registration, permissions, URL callbacks, session lifecycle, privacy controls, and testable unavailable states. Use when adding or reviewing DAT iOS code.
---

# Meta DAT iOS integration

Build the smallest native iOS adapter around the official DAT package. Keep registration/session state out of view code, keep the phone useful without glasses, and make every SDK assumption traceable to the selected source snapshot.

## Read before acting

- Inspect the actual `.xcodeproj`/`.xcworkspace`, app target, deployment target, Swift tools/Xcode version, package graph, Info.plist, entitlements, privacy manifest, app lifecycle, and existing adapters.
- Read [DAT iOS SDK foundations](../../../70-meta-wearables/01-dat-ios-sdk-foundations.md), [registration and permissions](../../../70-meta-wearables/02-registration-permissions-and-configuration.md), and [mock-device testing](../../../70-meta-wearables/07-mockdevice-testing-and-evidence.md).
- Read the [DAT iOS API surface atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md) and [upstream skill/tooling map](../../../70-meta-wearables/11-upstream-skill-and-tooling-map.md) before using a module or migration-specific symbol.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when registration, firmware, companion, on-glasses DAT-app provisioning, Developer Mode, release-channel, thermal, or recovery behavior is in scope.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when Info.plist identity keys, Meta AI callbacks, Developer Mode/release attestation, signing, or App Store/privacy-manifest review is in scope.
- Read the [debugging and observability route](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when registration, readiness, companion-boundary, device-path, session, stream, or typed-error diagnosis is in scope.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the native target includes Display input or a claim about native IMU/gesture sensors.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) before placing the adapter behind shared product state or a phone fallback.
- Pin or otherwise record the selected official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios) tag/commit. On the 2026-08-22 refresh, `main` was `225f64ff1617e7acc8c407bb8d3ee132f7263d00` while the 0.9.0 tag was `9b1b83d791dfebff7afd452e924a256819094b64`; use the tag for reproducible package resolution and validate its migration notes in the [changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) against the actual package graph.
- Read the official [iOS integration](https://wearables.developer.meta.com/docs/build-integration-ios), [permissions/registration](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/permissions-registration), and [session lifecycle](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/session-lifecycle) guidance.
- For camera/photo implementation, begin with the [source-aligned iOS camera starter](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift) after validating the selected SPM products and target privacy configuration.
- For deterministic fixture work, begin with the [source-aligned iOS MockDevice starter](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift) after linking the selected `MWDATMockDevice` product; keep its mock evidence separate from physical-device evidence.
- For XCUITest-process control, use the [source-aligned iOS MockDevice test-client starter](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift) with the app-owned test-server setup; keep `MWDATMockDeviceTestClient` test-only and separate from runtime app capability code.

## Integration workflow

1. Record the target, iOS deployment target, DAT tag/commit, device types, and requested capabilities.
2. Add the package using the official integration path and verify the actual products/modules exposed by that tag. Do not copy a product name from a different release.
3. Implement a narrow adapter with explicit states: `unconfigured`, `registrationRequired`, `registering`, `permissionRequired`, `ready`, `startingSession`, `connected`, `stopping`, `disconnected`, `unsupported`, `denied`, and `failed` as applicable to the installed API.
4. Put callback/deep-link configuration, permission requests, and registration recovery in the app integration boundary. Keep SwiftUI views as projections of state.
5. Start device sessions only from an intentional user flow or a documented product policy. Stop streams and release resources on cancellation, disconnect, and lifecycle transitions required by the SDK.
6. Treat SDK `stateStream`/`errorStream` completion and stopped-session behavior as part of the contract; test cancellation and reconnect rather than only the happy path.
7. Verify analytics/crash settings and data-handling policy. Current DAT notes distinguish opt-out controls from always-enabled device access management; use the selected release’s wording and settings.
8. Add mock fixtures and an unavailable phone-only path before connecting camera, audio, or Display features.

## 0.9 migration traps to check

When the selected package is 0.9.0 or later, explicitly review the official changelog for:

- `DeviceSession.addCamera(config:)` and the child `Camera.stream`/`Camera.stop()` lifecycle;
- removal of the older `addStream(config:)` path;
- stream/state/error completion when a session stops;
- `DeviceType.supportsDisplay` and Display button-group changes;
- iOS minimum version, mock-link behavior, and camera sample background handling;
- `ListenerTokenBag` actor/`AnyListenerToken.store(in:)`, synchronous
  `MockCameraKit.setCameraFeed(cameraFacing:)`, doff/`hingesClosed`, and
  terminal stream completion;
- crash-reporting and device-access-management configuration changes.

These are review prompts, not permission to use an API without compiling against the selected tag.

## Fast path

Run target preflight and resolve the exact SPM product before implementation. Then prove one lifecycle from registration and permission through a started session to capability stop; keep camera, Display, mock, and physical proof as separate follow-on gates.

## Required output

Return:

- package/tag/commit and actual module/product names;
- target configuration and callback/permission inventory;
- adapter state machine and lifecycle table;
- mock and build-test plan;
- privacy/data-handling decisions;
- exact unresolved API or device questions.

## Hard boundaries

- Do not put registration or permission calls in a view initializer.
- Do not treat pairing as a permanent authorization; model denial, revocation, disconnect, and re-registration.
- Do not log access tokens, callback URLs containing secrets, raw media, or persistent device identifiers.
- Do not claim a device is supported because the package compiles; runtime model/capability and hardware proof are separate.
- Do not assume iOS background execution, Meta AI voice commands, or raw glasses audio from DAT’s existence.

## Related routes

- [Meta route planner](../meta-wearables-route-planner/SKILL.md)
- [Camera and audio](../meta-dat-camera-audio/SKILL.md)
- [Display](../meta-dat-display/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Apple system surfaces](../ios-system-surfaces-and-background/SKILL.md)
- [Apple privacy and security](../ios-privacy-performance-release-proof/SKILL.md)

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS permissions and registration skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/permissions-registration)
- [DAT iOS session lifecycle skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/session-lifecycle)
- [DAT iOS sample-app guide](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/sample-app-guide)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Build integration for iOS](https://wearables.developer.meta.com/docs/build-integration-ios)
- [Apple app life cycle](https://developer.apple.com/documentation/uikit/managing-your-app-s-life-cycle)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
