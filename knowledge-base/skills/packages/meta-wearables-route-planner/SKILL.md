---
name: meta-wearables-route-planner
description: Choose the correct Meta Wearables route across native iOS DAT, native Display, Ray-Ban Display Web Apps, phone fallback, and unsupported or unverified device requests. Use before implementation whenever a product mentions Ray-Ban Meta, Oakley Meta, Meta Glasses, Display, camera, audio, input, sensors, Gen 2, Gen 3, or the Meta Wearables SDK.
---

# Meta Wearables route planner

Turn a wearable idea into a verified platform route before package imports, UI work, permissions, or marketing copy harden around an assumption.

## Read before acting

- Inspect the actual project, target platforms, deployment target, existing device integrations, and whether the requested surface is a companion app or a glasses-delivered experience.
- Read [platform and route selection](../../../70-meta-wearables/00-platform-and-route-selection.md), [device models and capability matrix](../../../70-meta-wearables/05-device-models-and-capability-matrix.md), and [the Meta source registry](../../../sources/meta-wearables-source-registry.md).
- Read the [device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) when product wording includes Gen 2, Gen 3, Meta Glasses, Display, or an SDK alias.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) when wording includes firmware, companion/DAT-app version, support matrix, or compatibility failure.
- Read the [full SDK capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md) when the request says “full,” “regular SDK,” “all capabilities,” or parity.
- Load the portable [surface manifest](../meta-wearables-full-sdk-audit/references/surface-manifest.yaml) and resolve its `terminology_contract` before selecting a route; preserve ambiguous or unresolved status instead of translating user labels into SDK symbols.
- Read the [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md) when Android/Kotlin/Java symbols, Maven coordinates, or 0.9 migration behavior is in scope.
- Read [Developer Center project and release operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md) when account/team/project identity, tester access, versions, release channels, or telemetry is part of the route.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) when the capability or failure involves Bluetooth, Wi-Fi/local network, HFP/A2DP, latency, backpressure, thermal/power, or link recovery.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) when the request says “on-device,” “local-first,” private, offline, low-latency, or asks where processing occurs.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when the request includes firmware, companion versions, Developer Mode, release channels, update-required/device-unavailable errors, or recovery.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when more than one surface, platform, capability, or phone fallback will share product behavior.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the outcome depends on Display actions, D-pad/captouch, Neural Band/EMG, temple gestures, motion/orientation, geolocation, browser sensors, or an “on-device” sensor claim.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when the outcome depends on bundle/package identity, Meta AI callbacks, Developer Mode, release channels, app attestation, credentials, Web App origin, privacy-manifest/App Store gates, or an “on-device” trust claim.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/), and [Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps).
- If the request says “regular SDK,” resolve the phrase against the current official docs and repository. Do not invent a second native iOS SDK or silently substitute Web Apps for DAT.

## Fast path

Resolve one request through the route map: exact surface, capability, runtime, fallback, and evidence. If labels such as “regular SDK” or “Gen 3” remain ambiguous, return a blocked or `to-verify` route instead of branching into every lane.

## Route map

| User outcome | Candidate route | Choose it when | First gate |
| --- | --- | --- | --- |
| iOS app discovers/uses supported glasses capabilities | native DAT iOS | the capability is exposed by the current DAT package and device | package/API and registration availability |
| Android app discovers/uses supported glasses capabilities | native DAT Android | the capability is exposed by the selected Maven artifact and device | Gradle/API and registration availability |
| glanceable native surface from the companion app | DAT Display | runtime device reports Display support | `DeviceType.supportsDisplay()` and physical model |
| HTML/CSS/JS experience delivered to Ray-Ban Display | Meta Wearables Web App | the target is explicitly the Web App surface | public HTTPS URL, 600×600, input/focus contract |
| wearer input, motion, orientation, or location | native Display, Web App, or phone fallback | the exact source is identified and the selected runtime exposes it | source/capability/permission or secure-context gate plus physical task |
| setup, consent, unavailable state, or unsupported device | phone-first fallback | wearable is absent, denied, disconnected, or not proven | useful phone workflow without wearable |
| “Gen 3 support” or unnamed future model | to-verify / blocked | official source and runtime mapping are missing | exact device type, firmware, capability, hardware |

The native DAT route and Web App route can coexist in one product, but they have different packages, lifecycle, deployment, and proof requirements.

## Planning workflow

1. Rewrite the request as an outcome, not a device label: capture, show, notify, navigate, control, or configure.
2. Identify the delivery surface: iOS companion, native glasses Display, Ray-Ban Display Web App, or phone fallback.
3. Record the exact device wording and map it to the runtime `DeviceType` only when an official source or observed device proves the mapping.
4. Identify the capability: registration, camera, audio, Display, button/input, Wi-Fi, or another named API. Mark undocumented behavior `to-verify`.
5. Define the permission, consent, privacy, session, disconnect, cancellation, and unavailable states.
6. Freeze the operational tuple when the route depends on companion, firmware,
   on-glasses DAT-app provisioning, release-channel, thermal, or transport state.
7. Select the shared domain/coordinator and platform adapter boundaries before
   assigning implementation files; keep Web Apps and native DAT separate.
8. Select the smallest specialist team and write a handoff with sources, version, and evidence requirements.
9. Reject routes that depend on a public API, model, entitlement, background behavior, or voice feature that the current sources do not establish.

## Compatibility language

Use these labels in plans and code reviews:

- **Documented** — present in the cited official API or product documentation.
- **Build-proven** — the exact target compiles or tests against the cited package/version.
- **Mock-proven** — the SDK mock or simulator exercises the path.
- **Connected-device proven** — a paired device completed the path, with model/firmware recorded.
- **Physical Display proven** — the actual glasses rendered and accepted the interaction.
- **To verify** — an open question; never write it as a supported feature.

## Required output

Return:

- route and rejected alternatives;
- exact SDK/repository/tag or commit;
- device/model/capability table;
- phone and wearable state machine;
- permissions/privacy and data-flow questions;
- firmware/companion/provisioning/release-channel and recovery questions;
- implementation owners and evidence ladder;
- explicit `Gen 3` and “regular SDK” resolution status.
- the manifest terminology status and the exact canonical route selected from it.

## Hard boundaries

- product-generation names map one-to-one to SDK enums;
- every Ray-Ban Meta or Oakley Meta model has a Display, camera, audio, or Wi-Fi capability;
- Web Apps can use native DAT APIs directly;
- a simulator, browser, or phone camera proves glasses behavior;
- Meta AI voice commands are part of the current public DAT preview;
- an undocumented “regular SDK” is interchangeable with DAT.

## Related routes

- [Meta Wearables agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT camera and audio](../meta-dat-camera-audio/SKILL.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [device proof](../meta-wearables-device-proof/SKILL.md)
- [on-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [application architecture](../meta-wearables-app-architecture/SKILL.md)
- [security and attestation](../meta-wearables-security-attestation/SKILL.md)

## Sources

- [Meta Wearables DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta Wearables DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md)
- [Developer Center operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md)
- [Security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Introducing Meta Wearables Device Access Toolkit](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/)
- [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
