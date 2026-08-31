---
name: meta-wearables-device-proof
description: Plan and audit reproducible target preflight and evidence for Meta Wearables apps across source inspection, iOS/Android/Web App inventory, unit/build checks, DAT MockDevice, browser simulator, connected-device tests, and physical Ray-Ban/Oakley/Meta glasses. Use whenever a result could be mistaken for hardware, model, camera, audio, Display, input, or release proof.
---

# Meta Wearables device proof

Keep simulated, connected, and physical observations separate. The purpose of this skill is to prevent a passing build or mock from becoming an unsupported product claim.

## Read before acting

- Inspect the actual target, SDK tag/commit, test scheme, mock/simulator setup, and available hardware/account access.
- Read [MockDevice testing and evidence](../../../70-meta-wearables/07-mockdevice-testing-and-evidence.md), [device models and capabilities](../../../70-meta-wearables/05-device-models-and-capability-matrix.md), and [privacy/publishing](../../../70-meta-wearables/08-privacy-publishing-and-release.md).
- Read the [device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) before naming a generation or interpreting a model enum.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) before naming firmware support, interpreting a compatibility failure, or promoting Gen 2/Gen 3 evidence.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) when the claim includes local processing, raw-data handling, thermal safety, or fallback behavior.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the named task includes Display actions, D-pad/EMG/temple gestures, motion/orientation, geolocation, or sensor quality.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when the run includes firmware, companion, on-glasses DAT-app provisioning, release-channel, update-required, thermal/power, or recovery behavior.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when the evidence claim depends on shared reducers, adapter fakes, capability ownership, or fallback seams.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) when the script includes Bluetooth/Wi-Fi, HFP/A2DP, sustained streaming, route changes, thermal/power, or link recovery.
- Read [debugging, observability, and diagnostic evidence](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) for app-visible DAT readiness, first-failure, event-digest, and redacted diagnostic evidence.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when a proof run depends on callback identity, Developer Mode/release attestation, signed artifacts, tester/channel access, or redacted credentials.
- Run the bundled [target-surface inspector](scripts/inspect_target_surfaces.py) against the actual target workspace before loading the target-preflight reference. If the knowledge base is a separate sibling, pass that app root to the inspector and to the team runner’s `--target-root`. `TARGETS_PRESENT` permits target-specific preflight; `TARGETS_PARTIAL` and `NO_TARGET` require the project bootstrap packet.
- When an iOS `TARGETS_PRESENT` target exists, run the bundled [redacted iOS target receipt runner](scripts/run_ios_target_preflight.py) with an explicit project/workspace, scheme, configuration, and destination. Use `--test` only for an intentional build/test observation; its JSON receipt contains safe settings and package-lock facts, never raw xcodebuild output or credential values.
- When an Android `TARGETS_PRESENT` target exists, run the bundled [redacted Android target receipt runner](scripts/run_android_target_preflight.py) with the actual Gradle root, module, variant, and route. It inventories the target-owned build graph, DAT coordinates, manifest keys, source migration markers, toolchain signals, and credential presence without printing values or resolving/publishing dependencies. A static pass is not an Android compile or device result.
- When iOS UI tests need cross-process MockDevice control, use the [source-aligned MockDevice test-client starter](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift) and record the app-process test-server setup, UI-test client, sanitized state/actions, and teardown separately. `MWDATMockDeviceTestClient` is test-only evidence and never a physical-device result.
- Use the [workspace device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md) for the full route matrix, and read the portable [execution reference](references/execution-packet.md) when the package is used outside this workspace.
- Load the [capability/evidence plan](../meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml) for the selected capability; carry its required evidence levels and proof task IDs into the run instead of inventing a local task list.
- Read the portable [target-preflight reference](references/target-preflight.md) before `BUILD-01`, `REL-01`, `PRE-*`, connected, physical, or release work; run `python3 scripts/validate_target_preflight.py` after editing it.
- Refresh the official [DAT iOS MockDevice skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/mockdevice-testing), [Mock Device Kit](https://wearables.developer.meta.com/docs/mock-device-kit), and [iOS testing guidance](https://wearables.developer.meta.com/docs/testing-mdk-ios).
- Check the current [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) for mock-link and device-model behavior before relying on an older fixture.

## Fast path

Run the target-surface inspector, then only the lowest unmet `PRE-*` prerequisite for the named claim. Promote evidence one level at a time with exact target, build, device, time, and result; stop when a required gate is missing instead of rerunning downstream steps.

## Evidence ladder

| Level | What it proves | What it does not prove |
| --- | --- | --- |
| source | an official API/product rule is documented | package compiles or device supports it |
| static/config | target files, permissions, URL, privacy, or package wiring are present | runtime registration or hardware behavior |
| build/test | exact code compiles and automated tests pass | glasses rendering, radio, camera, audio, Display, or ergonomics |
| mock | adapter state/error paths respond to controlled device events | physical timing, brightness, firmware, real input, or sensor/media quality |
| browser simulator | Web App layout/input logic in the simulator | deployed URL and physical Display behavior |
| connected device | a named paired model completed the observed path | other models, future generations, or release readiness |
| physical release proof | the target glasses completed the scripted flow with artifacts | untested models, claims beyond the script, or App Store approval |

## Proof workflow

1. Freeze the source snapshot: SDK version, repository commit/tag, docs date, target commit, build configuration.
2. Record the exact `DeviceType`, product/model name, firmware, phone OS, app build, and account/access condition when known.
3. Run the target preflight: freeze the actual iOS scheme/target and
   `Package.resolved`, Android module/variant and resolved Maven graph, or Web
   App revision/origin/input configuration. Redact secrets before storing it.
4. Run static/config checks for package products, callback, permissions, entitlements, privacy manifest, URL, and fallback.
5. Run unit/integration tests with deterministic mock events: register, permission denied, session start/stop, disconnect, error, camera/audio stop, Display unsupported, and input actions.
6. Run the browser simulator for Web Apps and record URL, canvas, focus, input, loading, error, and performance observations.
   Keep text composer, offline cache, Escape/back, extended gestures, and
   sensors as separate `source-conflict`/`to-verify` rows because the current
   public index and toolkit `main` disagree about them.
7. Run connected-device tests when a supported device is available. Capture only sanitized evidence: model/firmware, test ID, result, timestamp, and relevant error code.
8. Run the physical script on the exact target before claiming real camera, audio, Display, button/D-pad/EMG, Wi-Fi, latency, or comfort behavior.
9. For a failure or update-required result, preserve the first failing state,
   apply one documented recovery, and record the post-action state; distinguish
   `recovery-attempted` from `recovery-observed`.
10. Fill one sanitized result record per packet task. Use the packet’s artifact and redaction contract; never retain raw media or device identifiers merely to make a run reproducible.
11. Mark every unrun step `not run` or `to verify`; never convert it to pass because a neighboring step passed.

## Physical script minimum

- registration and permission recovery;
- session connect, disconnect, and reconnect;
- phone fallback with the glasses absent;
- camera/audio start and clean stop if in scope;
- Display render, focus, primary action, back/dismiss, timeout, and disconnect if in scope;
- Web App launch, 600×600 layout, focus, D-pad/available input, loading, error, and exit if in scope;
- thermal/battery/latency observations proportional to the feature;
- companion/firmware/on-glasses DAT-app, mode/channel, first failure, recovery action, and post-action state;
- no private media or identifiers in screenshots/logs.

## Required output

Return the target-surface inspector receipt, a preflight summary, the selected capability/evidence-plan entry, and an evidence matrix. Every row contains:
feature, exact target, source, test level, observed result, artifact pointer, and
remaining gate. Include the `PRE-*` status before promoting any build or device
claim.

## Hard boundaries

- Do not call simulator, mock, or iPhone-only behavior “on-device glasses support.”
- Do not generalize a result from Ray-Ban to Oakley or from one generation to another.
- Do not use production credentials, raw personal media, or unredacted device identifiers in fixtures.
- Do not announce release readiness while required physical, privacy, access, or publishing gates remain open.
- Do not upgrade a Web App toolkit feature to supported merely because it works
  in a desktop simulator; close the current Developer Center/toolkit conflict
  on the exact firmware or keep the documented fallback.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
- [Device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [On-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [Operational readiness and recovery](../../../70-meta-wearables/18-operational-readiness-and-recovery.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Application architecture and platform boundaries](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md)
- [Target preflight reference](references/target-preflight.md)
- [Redacted iOS target receipt runner](scripts/run_ios_target_preflight.py)
- [Redacted Android target receipt runner](scripts/run_android_target_preflight.py)
- [iOS device release proof](../ios-device-release-proof/SKILL.md)
- [iOS testing and release assurance](../ios-testing-and-release-assurance/SKILL.md)

## Sources

- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/mockdevice-testing)
- [Meta Mock Device Kit](https://wearables.developer.meta.com/docs/mock-device-kit)
- [Testing with the Mock Device Kit on iOS](https://wearables.developer.meta.com/docs/testing-mdk-ios)
- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Apple target build settings](https://developer.apple.com/documentation/xcode/configuring-the-build-settings-of-a-target/)
- [Apple Swift package CI/build guidance](https://developer.apple.com/documentation/xcode/building-swift-packages-or-apps-that-use-them-in-continuous-integration-workflows)
- [Gradle dependencyInsight](https://docs.gradle.org/current/userguide/command_line_interface.html)
