---
name: meta-wearables-operational-readiness
description: Diagnose and harden Meta Wearables DAT iOS, DAT Android, native Display, and Ray-Ban Display Web App integrations across firmware, Meta AI companion, Developer Mode, release channels, DAT app provisioning, compatibility, thermal and link failures, and recovery evidence. Use when an integration will not register, cannot start a session, reports an update or device-unavailable error, moves from Developer Mode to a signed release channel, or needs a repeatable operational-readiness packet.
---

# Meta Wearables operational readiness

Act as the reliability and release-operations specialist for Meta Wearables.
Make the entire tuple—mobile app, DAT artifact, Meta AI companion, glasses
firmware, on-glasses DAT app, account/project, transport, and release channel—
explicit before diagnosing a failure or calling a route ready.

## Read before acting

- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md), [device/release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md), [full-SDK matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), [generation matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md), and [on-device contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md).
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) for exact firmware/companion/artifact tuples, access-gated dependency values, community-signal classification, and `COMP-*` evidence.
- Read the [portable recovery contract](references/recovery-contract.md) before collecting a run packet or writing a recovery recommendation.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) when the failure involves Bluetooth, Wi-Fi/local network, HFP/A2DP, queue pressure, route changes, thermal/power, or sustained streaming.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when readiness or recovery affects Display input, D-pad/EMG/temple gestures, browser sensors, permissions, or sensor watches.
- Read [debugging, observability, and diagnostic evidence](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when a DAT readiness, registration, permission, device-path, session, stream, or recovery failure needs app-visible diagnosis.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when diagnosing ownership, stale events, fallback, or lifecycle recovery across multiple platform adapters.
- Read [Developer Center project and release operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md) when failure behavior involves project build status, tester/channel access, app identity, telemetry, or account recovery.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when the failure involves callback configuration, identity keys, Developer Mode, release attestation, package/signing credentials, or App Store/privacy-manifest gates.
- Refresh the pinned [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [full DAT reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat), [version dependencies](https://wearables.developer.meta.com/docs/version-dependencies), [known issues](https://wearables.developer.meta.com/docs/knownissues), and [release-channel guidance](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/) before a version-sensitive run. Authenticated or access-gated tables remain `to-verify` until the account view is observed.
- Inspect the actual target’s package/artifact graph, deployment/min SDK, configuration, permissions, privacy manifest/manifest, signing identity, and URL callback before changing code.

## Operational workflow

1. **Freeze the tuple.** Record platform, app target/build, SDK package or Maven artifact, repository/tag, phone OS, Meta AI version, exact product label, runtime model/`DeviceType`, firmware, on-glasses DAT app state/version if visible, account/project, mode, and requested operation. Redact tokens, bundle identifiers when sensitive, serials, and raw diagnostics.
2. **Classify the mode.** Keep Developer Mode, a signed release-channel build, a simulator/browser run, and production separate. Developer Mode can make registration available without proving release-channel authorization, app attestation, provisioning, or store readiness.
3. **Preflight compatibility.** Compare every tuple member against the current official version-dependency surface. Label each value `source`, `static`, `observed`, `access-gated`, `conflict`, or `unknown`; never resolve a conflict by guessing.
4. **Trace provisioning.** Check Meta AI installation, account/project membership, Developer Mode, registration state, permissions, application ID/signature/client configuration, link state, compatibility, and whether the on-glasses DAT app needs an update. Use the documented firmware/DAT-app navigation APIs only when the selected artifact exposes them.
5. **Run one controlled operation.** Capture the ordered events for registration, session start, camera/Display/audio action, pause/disconnect, recovery, and stop. Do not loop retries through thermal, battery, power, doff, or unknown protocol failures.
6. **Apply typed recovery.** Distinguish configuration, account/channel, companion, firmware, on-glasses DAT app, transport, permission, lifecycle, thermal/power, and SDK/API failures. Apply the least invasive documented recovery, then re-run the same operation with a new run ID.
7. **Audit release readiness.** Re-test with the signed artifact, release channel, tester account, exact firmware, and physical pair. A clean Developer Mode run is not release evidence.
8. **Return the packet.** Produce the compatibility tuple, event trace, diagnosis, recovery attempted, evidence level, remaining gates, and next source-refresh trigger.

## Fast path

Use this first-failure order: identity/access -> companion/firmware tuple -> mode/channel -> session/capability -> transport/thermal -> recovery. Capture the current state before repair and verify the post-state once; avoid repeated resets that erase the diagnostic boundary.

## Required output

- target and version tuple with source/observed/access-gated labels;
- Developer Mode versus release-channel decision;
- preflight matrix for companion, firmware, DAT app, account/project, transport, permissions, and SDK artifact;
- ordered event trace and exact first failing state/error;
- bounded recovery action and whether it was actually observed to work;
- thermal, battery, doff/fold, disconnect, app-background, and stop behavior;
- redacted evidence ledger using `OPS-SOURCE-01` through `OPS-CHANNEL-01` where applicable;
- explicit `ready`, `ready-for-device`, `blocked`, `source-conflict`, or `to-verify` result.

## Hard boundaries

- Never treat a GitHub issue, discussion, or user report as an official compatibility guarantee; it is a troubleshooting signal that must be labeled separately.
- Never print or commit Meta application IDs, client tokens, app signatures, account emails, device serials, raw media, or diagnostic bundles.
- Never claim firmware or Meta AI compatibility from a neighboring version, consumer generation name, or a stale example.
- Never equate Developer Mode with release-channel authorization, app attestation, signed distribution, Store approval, or production readiness.
- Never expose callback payloads, client/package credentials, app signatures, or
  private project identifiers while diagnosing identity or channel failures.
  Attestation and channel state do not prove local processing or physical
  capability.
- Never auto-retry through thermal emergency, battery critical, peak-power shutdown, doff/hinge closure, or an unknown protocol error; stop, preserve the event trace, and require a deliberate recovery.
- Never map `Gen 3` to a DAT `DeviceType`, Meta Glasses, Display, or another model without current official mapping plus named runtime evidence.
- Never call an on-glasses DAT-app update, firmware update, or re-pair successful unless the target reports the post-action state and the original operation completes.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Full-SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)

## Sources

- [Operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md)
- [Device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Wearables known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Wearables release-channel guidance](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/)
- [Security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
