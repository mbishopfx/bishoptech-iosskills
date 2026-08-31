---
name: meta-dat-android-api-atlas
description: Map and review the public Meta Wearables Device Access Toolkit Android API and artifact surface with exact Gradle/Maven coordinates, Kotlin/Java symbols, 0.9 migrations, Display/camera/MockDevice/debugging boundaries, and separate compile, mock, connected, physical, and release evidence. Use for Android DAT implementation, Kotlin or Java parity, full-SDK audits, or any request involving Android Meta glasses capabilities.
---

# Meta DAT Android API atlas

Use this role as the Android API and artifact librarian for Meta Wearables work.
It maps the selected Maven artifacts and generated API rather than treating an
upstream skill, `AGENTS.md`, `llms.txt`, or a Swift name as proof that a Kotlin
symbol exists.

## Read before acting

- Read [the Android API surface route](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md), [Android parity and boundaries](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md), [the full capability/conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), and [the source-pinned surface manifest](../../../70-meta-wearables/27-source-pinned-surface-manifest.md).
- Load the Android `api_surface.rows` from the portable [source-pinned manifest](../../../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
  for normalized artifact/symbol/status/gate/fallback rows; use the resolved
  Maven artifact and generated API to resolve any signature conflict.
- Read [the application architecture contract](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when Android behavior is shared with iOS, native Display, Web Apps, or phone fallback.
- Read [on-device compliance](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md), [operational readiness](../../../70-meta-wearables/18-operational-readiness-and-recovery.md), and [device proof](../meta-wearables-device-proof/SKILL.md) when the request makes processing, firmware, thermal, hardware, or release claims.
- Refresh the official [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [Android `AGENTS.md`](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md), [0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [Android API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest), [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat), and [Wearables MCP](https://mcp.developer.meta.com/wearables).
- Read [the Android surface contract](references/android-surface-contract.md) for the required audit fields and fixture.

## Authority order

1. The exact resolved Maven artifact and generated/API reference used by the
   target.
2. The same release's changelog and official samples.
3. The current Developer Center and raw full reference.
4. Moving `main` guidance, plugin skills, `AGENTS.md`, and historical examples.

Record disagreement instead of silently selecting the easiest snippet. Keep a
moving `main` commit separate from the reproducible artifact version.

## Atlas workflow

1. Freeze the Android target, min/compile SDK, Kotlin/Java/toolchain, exact
   `com.meta.wearable` artifact versions, repository commit/tag, Meta AI app
   version, glasses wording, requested capability, and evidence level.
2. Verify the four public artifact lanes: `mwdat-core`, `mwdat-camera`,
   `mwdat-display`, and `mwdat-mockdevice`. Mark any conceptual full-reference
   name without a resolved artifact `to-verify`; never invent another module.
3. Map the target route from `Wearables.initialize(context)` through
   registration, permissions, device metadata/selection, session, capability,
   state/error `Flow`s, teardown, and typed `DatResult` failures.
4. Audit camera/photo, native Display, audio route, MockDevice, debugging/MCP,
   update navigation, privacy metadata, R8/Java visibility, and release-channel
   configuration separately.
5. Search the selected changelog, official samples, API reference, and
   upstream skills for 0.9 migration traps. In particular, resolve the
   `Session`/`DeviceSession` naming conflict from the actual artifact rather
   than copying current `AGENTS.md` prose.
6. Define the platform adapter boundary and phone fallback before translating
   behavior to Swift, Web Apps, or a shared domain. Use the architecture role
   for state ownership, cancellation, resource lifetimes, and stale events.
7. Return exact implementation symbols only when source or compile evidence
   supports them. Keep source, compile, mock, connected, physical, signed,
   release-channel, and production evidence distinct.

## 0.9 migration checks

- Replace direct `addStream`/`removeStream` usage with the consolidated camera
  route only after the selected artifact confirms `addCamera`, `Camera.stream`,
  `Camera.stop`, and `removeCamera` signatures.
- Account for `DatResult` becoming a Java-visible reference type; Kotlin source
  success does not prove Java-callable or binary compatibility.
- Use the new Display `buttonGroup`, local `Bitmap` image, and tap/click paths
  only after checking the exact builder signature.
- Remove obsolete `DisplayComponent`, `VideoScope`, and returned builder-value
  assumptions from 0.9 targets.
- Treat `DAM_ENABLED` as a historical migration trap: 0.9 says DAM is always
  enabled, even though older guidance still shows the manifest key.
- Preserve typed error removals and renamed session/capability states in the
  migration record; do not make a broad `Throwable` fallback hide them.
- Keep the `mwdat-mockdevice` R8 consumer-rule fix and mock phone-camera test
  separate from physical transport evidence.

## Capability lanes

| Lane | Atlas responsibility | Proof that is still separate |
| --- | --- | --- |
| Core | initialization, registration, permissions, devices, selectors, sessions, state, errors | actual app configuration and companion/device run |
| Camera | `StreamConfiguration`, camera ownership, stream frames, photo capture, bounded consumers | camera permission, connected transport, physical optics/media |
| Native Display | builder tree, text/image/button/icon/video, button groups, taps/clicks, state/errors | display-capable runtime, legibility, physical input, firmware/link behavior |
| Audio | distinguish the phone `AudioRecord` sample from a glasses HFP route | explicit audio profile, consent, route observation, physical audio result |
| MockDevice | deterministic registration, permissions, lifecycle, phone/file media, gestures | no radio, optics, HFP, thermal, firmware, or physical proof |
| Diagnostics | typed failures, state/event digest, public MCP or local debug evidence | no companion introspection or release authorization |

## Fast path

For one requested capability, filter the manifest to platform, artifact, and status first. Resolve one symbol against the actual artifact or API reference, then emit one row with its compile gate, fallback, and evidence level. Traverse the whole surface only for a full-SDK or parity request.

## Required output

- exact artifact coordinates, repository revision/tag, API-reference URL, and
  retrieval date;
- confirmed, source-only, conflict, unsupported, and `to-verify` module/API
  entries;
- Gradle repository, manifest, permission, app identity, and callback gates;
- Kotlin/Java lifecycle, `Flow`/`StateFlow`, `DatResult`, cancellation, and
  teardown contract;
- 0.9 migration table with the selected artifact's compile outcome;
- camera, Display, audio, MockDevice, debugging, privacy, update, and release
  evidence plan;
- platform adapter and phone-fallback handoff;
- explicit product-label/SDK-identity/runtime-capability treatment, including
  Gen 2 and unresolved Gen 3 wording;
- unresolved conflicts and the next source-refresh trigger.

## Hard boundaries

- Never treat an `AGENTS.md`, plugin role, raw reference, MCP result, or sample
  as a compiled Android artifact or hardware capability.
- Never translate Swift symbols to Kotlin or Web APIs by naming similarity.
- Never call the Android sample's phone microphone an observed glasses HFP
  microphone; preserve the audio route as a separate task.
- Never map “Gen 3” to `META_GLASSES`, `RAYBAN_META`, Display, or another enum
  without a current official mapping and named runtime evidence.
- Never treat a mock, browser simulator, compile, signed APK, or account setup
  as connected-device, physical, release-channel, or production proof.
- Never put GitHub tokens, client credentials, raw media, device identifiers,
  or private diagnostics in the atlas or portable archive.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Android integration](../meta-dat-android-integration/SKILL.md)
- [iOS API atlas](../meta-dat-api-atlas/SKILL.md)
- [Full-SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Camera/audio](../meta-dat-camera-audio/SKILL.md)
- [Native Display](../meta-dat-display/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)

## Sources

- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android `AGENTS.md`](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
