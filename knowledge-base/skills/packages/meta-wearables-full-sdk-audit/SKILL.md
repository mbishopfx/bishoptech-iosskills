---
name: meta-wearables-full-sdk-audit
description: Audit whether a Meta Wearables iOS, Android, or Ray-Ban Display Web App request actually covers the full public SDK surface, exact modules/artifacts, capability gates, upstream source conflicts, privacy boundaries, and required evidence. Use when a request says full SDK, regular SDK, all capabilities, Gen 2/Gen 3 support, or cross-platform parity.
---

# Meta Wearables full-SDK audit

Use this role before implementation when “full SDK,” “regular SDK,” “all
capabilities,” or cross-platform parity could hide an unverified module,
consumer feature, stale upstream example, or unsupported device claim.

## Read before acting

- Inspect the real iOS package graph or Android Gradle dependency graph, target
  settings, privacy files, and existing adapter.
- Read [the full capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), [the device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md), [the iOS API atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md), [the Android API atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md), [the plugin matrix](../../../70-meta-wearables/13-public-plugin-and-skill-matrix.md), and [the Android parity route](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md).
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) before treating IMU, EMG, temple, browser sensor, or Display input wording as a complete capability.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) before treating Gen 2/Gen 3, firmware, companion versions, or support-table values as resolved.
- Load the portable [source-pinned surface manifest](references/surface-manifest.yaml) before a full-SDK/parity audit; use it as a routing snapshot, never as generated API or hardware proof.
- Load the portable [Meta team manifest](../meta-wearables-agentic-team/references/team-manifest.yaml) and run `python3 ../meta-wearables-agentic-team/scripts/validate_team_manifest.py` in the workspace; use it to prove that selected upstream roles have local owners and device-claim gates.
- Resolve user wording through the manifest `terminology_contract` before routing; “regular SDK” is an ambiguous phrase, “full SDK” is a composite audit, and “Gen 3” remains an unresolved alias until official and named-device evidence close it.
- Load its `preflight_contract`, read the [target-preflight packet](../meta-wearables-device-proof/references/target-preflight.md), and select the relevant `PRE-*` tasks before build, connected, physical, signed, or release-channel work; preflight freezes facts but does not upgrade evidence.
- Load the portable [capability/evidence plan](references/capability-evidence-plan.yaml) and run `python3 scripts/validate_capability_evidence_plan.py`; use it to carry owner roles, implementation route, privacy path, fallback, minimum evidence levels, and proof task IDs for every selected capability.
- Filter `api_surface.rows` by the selected journey/platform and carry each row's source anchors, status, compile/runtime gate, privacy path, fallback, and migration note into the audit; these rows remain source routing, not generated-API or physical proof.
- Run `python3 scripts/validate_surface_manifest.py` after any manifest edit and before packaging; treat count, exact upstream plugin-role list, source-anchor, required-field, duplicate-ID, and secret-scan failures as refresh blockers.
- Run `python3 scripts/validate_capability_evidence_plan.py` after any capability/evidence-plan edit and before packaging; treat capability-ID, surface, preflight-task, evidence-task, level, duplicate, and secret-scan drift as blockers.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) for processing location, consent, raw-data, thermal, network, retention, and fallback claims.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) for firmware, companion, on-glasses DAT-app provisioning, Developer Mode versus release-channel, version-dependency, and recovery claims.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when the request spans iOS, Android, native Display, Web Apps, shared state, or a phone fallback.
- Read [Developer Center project and release operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md) when the request includes app identity, permission rationale, versions, channels, testers, telemetry, or release access.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when the request includes identity keys, callbacks, Developer Mode, release attestation, package/signing credentials, Web App origin, privacy-manifest/App Store gates, or an “on-device” trust claim.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) when the request includes Wi-Fi/local network, Bluetooth/link behavior, HFP/A2DP, backpressure, latency, thermal/power, disconnect, or recovery.
- Read [debugging, observability, and diagnostic evidence](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when the request includes a DAT failure, live DAT Inspector/MCP, readiness, event/error diagnosis, or a diagnostic handoff.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp), [full platform reference](https://wearables.developer.meta.com/llms.txt?full=true), and [Wearables MCP](https://mcp.developer.meta.com/wearables).
- Read [the capability audit fixture](references/capability-audit-fixture.md) when evaluating a “full SDK” or parity brief.

## Audit workflow

1. Freeze platform, target, OS/min SDK, package/artifact version, repository
   revision, Meta AI version, device wording, requested capabilities, and
   intended evidence level.
2. Load the source-pinned manifest, team manifest, resolve `terminology_contract`, and load the capability/evidence plan; select the
   matching journey, platform atlas, API-surface rows, capability row, mapped
   `PRE-*` tasks, owner role, implementation route, privacy path, fallback,
   minimum evidence levels, proof tasks, source conflicts, generation status,
   and evidence IDs before making a coverage claim.
3. Inventory the exact upstream plugin roles and agent-facing root surfaces from each manifest
   `source_inventory.<lane>.plugin_roles` list before mapping them to local
   handoffs; a role count without exact-name coverage is incomplete. Then
   verify the lane `AGENTS.md`, `README.md`, `install-skills.sh`,
   `.codex-plugin/plugin.json`, and public docs MCP references as source/tool
   routing inputs only. Then
   inventory native modules: iOS `MWDATCore`, `MWDATCamera`, `MWDATDisplay`,
   `MWDATMockDevice`, and the test-only `MWDATMockDeviceTestClient`; Android
   `mwdat-core`, `mwdat-camera`, `mwdat-display`, `mwdat-mockdevice`; and Web
   Apps as a separate hosted runtime. Keep test-process products separate from
   runtime capability claims.
4. Use the platform-specific API atlas to resolve exact iOS package products
   and Android Maven artifacts/symbols before comparing cross-platform concepts.
5. Map every requested capability to `current`, `to-verify`, `source-conflict`,
   `unsupported`, or a platform-specific fallback. Include registration,
   permissions, device selection, session, camera/photo, audio, Display,
   sensors, health/update, MockDevice, debugging, privacy, and release.
6. Search upstream `AGENTS.md`, plugin skills, samples, changelog, API
   reference, and MCP results for stale versions or conflicting symbol/config
   guidance. Let the selected artifact/API reference win only after recording
   the conflict and target build gate.
7. Separate consumer product wording, SDK model identity, and observed runtime
  capability. Treat “Gen 3” and “regular SDK” as unresolved until the current
  source and named target establish them.
8. Classify each data path as glasses-native, phone-local, remote, mixed, or
   unknown; audit consent, retention, lifecycle/thermal behavior, and the typed
   fallback for every requested capability.
9. For any registration, session, update, or release failure, freeze the full
   operational tuple and route the first failing state through the recovery
   contract; keep attempted recovery separate from observed recovery.
10. Define the shared product/domain contract and platform-specific adapter
   boundary; preserve iOS, Android, native Display, Web App, and phone fallback
   semantics rather than flattening them into a common symbol set.
11. Return the smallest implementation route, missing proof rows, phone/web
   fallback, compliance owner, privacy owner, and next source-refresh trigger.

## Fast path

Filter the request into platform, surface, and capability rows, run the terminology contract first, then count coverage and evidence gaps. Use a full-surface traversal only when the request is genuinely full or parity-focused; for one feature return selected rows plus the explicitly non-selected lanes.

## Required output

- exact source/package/artifact snapshot and date;
- manifest ID/revision, selected journey, and manifest rows used;
- team manifest ID/revision, selected local role IDs, upstream handoff IDs, and
  device-claim gates used;
- exact upstream iOS, Android, and Web Apps plugin-role lists, counts, and local
  handoff coverage;
- terminology-contract term, resolution status, canonical route candidates, and
  evidence boundary used to interpret the user’s device/SDK wording;
- selected preflight contract reference, applicable `PRE-*` task statuses, and
  redacted target/dependency/identity/data-path handoff;
- selected capability/evidence-plan entry with owner roles, implementation
  route, privacy path, fallback, required evidence levels, and proof task IDs;
- normalized API-surface row IDs used, including source anchors, status,
  compile/runtime gates, privacy paths, fallbacks, and migration notes;
- full-reference journey-section inventory covering setup/hardware, iOS,
  Android, Display, lifecycle/permissions, HFP/A2DP, MockDevice, AI/MCP/tooling,
  organization/project/release-channel administration, and Web Apps;
- full module and capability matrix with platform-specific symbols;
- dedicated iOS and Android API-atlas snapshots, including artifact/source/
  compile status and the Android `Session`/`DeviceSession` conflict;
- stale/conflicting source ledger and migration actions;
- product-label, SDK-identity, and runtime-capability matrix with explicit
  Gen 2, Meta Glasses, Display, and Gen 3 treatment;
- target, account, permission, privacy, device, firmware, and release gates;
- version-dependency access state, full phone/companion/on-glasses-DAT-app/
  firmware/artifact/runtime tuple, first-party versus community signal class,
  and `COMP-*` compatibility evidence rows;
- organization/team/project/platform-app, permission-rationale, version/build,
  tester/channel, telemetry, and account-recovery gates when distribution is in scope;
- processing-location, network/storage, consent, thermal/lifecycle, and fallback contract;
- transport-hop, iOS/Android configuration/parity, audio-route, queue/backpressure, thermal, and recovery contract;
- read-only debug-server/MCP baseline, first-failure graph, platform state/error map, narrow event digest, redaction review, and DBG evidence rows when diagnosis is in scope;
- operational tuple, Developer Mode/release-channel distinction, provisioning state, first failure, bounded recovery, and post-action evidence;
- shared state/event contract, platform adapter map, concurrency/resource ownership, stale-event strategy, and reducer/fake/mock/browser/physical test seams;
- mock/browser/connected/physical evidence plan;
- explicit Gen 2 mapping and Gen 3 `to-verify` status unless current official
  mapping and named-device evidence establish otherwise;
- unresolved gaps. Never return “full SDK” as an unqualified conclusion.

## Hard boundaries

- Never count a repository plugin role, `llms.txt` entry, or MCP search result as
  a compiled target module or hardware capability.
- Never translate Swift symbols into Kotlin or Web APIs by naming similarity.
- Never treat the Android sample’s phone `AudioRecord` as a glasses microphone,
  or the iOS HFP route as an Android DAT audio API.
- Never map “Gen 3” to `.metaGlasses`, `.rayBanMeta`, Display, or any product
  announcement without a current public mapping and named runtime evidence.
- Never call a mock, browser simulator, compile, account configuration, or
  signed artifact physical or production proof.
- Never include tokens, client credentials, raw media, device identifiers, or
  private diagnostic payloads in the audit or archive.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT API atlas](../meta-dat-api-atlas/SKILL.md)
- [DAT Android API atlas](../meta-dat-android-api-atlas/SKILL.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Device compatibility](../meta-wearables-device-compatibility/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)

## Sources

- [Full capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [Version-dependency and device-compatibility evidence](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md)
- [Source-pinned surface manifest route](../../../70-meta-wearables/27-source-pinned-surface-manifest.md)
- [Capability/evidence plan](references/capability-evidence-plan.yaml)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS AGENTS.md](https://github.com/facebook/meta-wearables-dat-ios/blob/main/AGENTS.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/)
- [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
