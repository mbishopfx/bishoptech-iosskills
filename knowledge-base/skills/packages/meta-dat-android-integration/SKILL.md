---
name: meta-dat-android-integration
description: Integrate and review the public Meta Wearables Device Access Toolkit for Android with exact Maven artifacts, Gradle/Manifest configuration, registration, typed DatResult flows, sessions, camera, Display, MockDevice, privacy, and separate physical-device evidence. Use when a request mentions DAT Android, Kotlin, Gradle, Android glasses integration, or cross-platform parity.
---

# Meta DAT Android integration

Use this role for the Android member of the Meta Wearables DAT family. Keep it
separate from DAT iOS: Android has Maven artifacts, Manifest metadata, Kotlin
`Flow`/`StateFlow`, and `DatResult` contracts that must be checked in the actual
Gradle target.

## Read before acting

- Inspect the real Android project, Gradle wrapper/version catalog, resolved
  Maven artifacts, Manifest, permissions, intent filters, min/target SDK,
  ProGuard/R8 rules, privacy disclosures, and existing adapters.
- Read [DAT Android parity and boundaries](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md), the [public plugin matrix](../../../70-meta-wearables/13-public-plugin-and-skill-matrix.md), and the [full SDK capability/conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md).
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when manifest identity, callback schemes, GitHub Packages credentials, Developer Mode/release attestation, signing, or Play/privacy review is in scope.
- Read the [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md) and its [surface contract](../meta-dat-android-api-atlas/references/android-surface-contract.md) before making exact symbol or 0.9 migration claims.
- Refresh the official [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md), [0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [Android API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest), and [Wearables MCP](https://mcp.developer.meta.com/wearables).
- Read the portable [Android migration fixture](references/android-api-migration.md) when reviewing a version-sensitive change.
- Use the official [0.9.0 DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess) and its [DisplayViewModel](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/DisplayAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/displayaccess/display/DisplayViewModel.kt) as the current source anchor for `DeviceSession`/Display shapes; older upstream `AGENTS.md`/plugin examples that say `Session` remain a compile-time source conflict.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when registration, firmware, companion, on-glasses DAT-app provisioning, Developer Mode, release-channel, thermal, or recovery behavior is in scope.
- Read the [debugging and observability route](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when Android readiness, registration, permission, device-path, `DatResult`, session, stream, or companion-boundary diagnosis is in scope.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the Android target includes Display input or a claim about native IMU/gesture sensors.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) before sharing Android behavior with iOS, native Display, Web Apps, or a phone fallback.
- Treat GitHub Packages credentials as opaque. Pass them through the approved
  environment/local-properties path; never print, commit, or place them in a
  fixture or archive.
- For camera/photo implementation, begin with the [source-aligned Android camera starter](../meta-wearables-implementation-recipes/assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt) after resolving the selected Maven artifacts and target configuration.
- For deterministic fixture work, begin with the [source-aligned Android MockDevice starter](../meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt) after resolving `mwdat-mockdevice`; keep instrumentation/mock evidence separate from connected and physical-device evidence.

## Integration workflow

1. Record the Android OS/min SDK, Gradle/AGP/Kotlin versions, exact DAT
   artifacts, device/model wording, Meta AI version, and requested capability.
2. Resolve only the required modules:
   `mwdat-core`, `mwdat-camera`, `mwdat-display`, and `mwdat-mockdevice`.
3. Initialize once with `Wearables.initialize(context)` and expose typed
   registration, permission, device, session, capability, and failure states to
   the app UI.
4. Use `DatResult` failures rather than `getOrThrow()` in user-facing paths;
   observe `Flow`/`StateFlow` with lifecycle-aware cancellation.
5. Attach `Camera` or `Display` only after a started session. Stop capabilities,
   cancel collectors/frame work, then stop the session on exit, disconnect,
   doff/fold, error, or cancellation.
6. Audit Manifest permissions, intent callback, application/client metadata,
   analytics/crash settings, privacy, network, and fallback before media access.
7. Run MockDevice and Gradle tests, then a named connected/physical device
   script. Do not convert iOS results or mock results into Android proof.

## 0.9 migration traps

- Use `addCamera()` → `Camera.stream`; do not use removed direct stream APIs.
- Review the `ButtonGroup`/local `Bitmap`/tap callback Display changes.
- Remove old DAM metadata and old `DisplayComponent`/`VideoScope` builder shapes.
- Check the Java-visible `DatResult` change if the app has Java callers.
- Preserve the camera stop order and target-specific background audio/video
  behavior; the sample is not a universal background guarantee.
- Include the MockDevice/R8 consumer-rule check in release builds.
- Treat upstream `AGENTS.md`/plugin examples as refresh inputs, not version
  authority: current examples contain 0.8.0 coordinates, older `Session`
  wording, and obsolete `DAM_ENABLED` guidance, while the 0.9.0 changelog and
  DisplayAccess sample establish the current `DeviceSession`/DAM behavior.
  Resolve the remaining names from the selected artifact/API reference.

## Fast path

Make the Android compile path explicit: resolve one artifact set -> initialize -> expose typed states -> attach one capability -> stop cleanly. Run target preflight and Gradle compile before adding parity or physical cases; if no Android target exists, return a bootstrap packet instead of inventing build evidence.

## Required output

- exact Maven artifact versions and resolved module graph;
- Android target, Manifest, credential, permission, callback, and privacy audit;
- Kotlin lifecycle/`DatResult`/`Flow` state contract;
- camera, Display, MockDevice, and failure test plan;
- iOS parity comparison with symbols explicitly labeled same-concept or
  platform-specific;
- evidence matrix separating source, Gradle build, fixture, connected, and
  physical results;
- unresolved device-generation, release-channel, and API-reference gates.

## Hard boundaries

- Never infer Kotlin signatures or Android support from iOS code.
- Never call the Android SDK “full” without checking all four modules and the
  capability/conflict matrix for the requested feature.
- Never print or persist GitHub Packages tokens, Developer Center credentials,
  raw media, device identifiers, or private release-channel details.
- Never call a phone/mock/Gradle result physical glasses proof.
- Never map “Gen 3” to an enum, product announcement, or neighboring model.
- Never claim Play/App Store approval, release-channel access, or production
  behavior from repository documentation.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT API atlas](../meta-dat-api-atlas/SKILL.md)
- [DAT Android API atlas](../meta-dat-android-api-atlas/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)

## Sources

- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
