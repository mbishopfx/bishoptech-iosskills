---
name: meta-wearables-on-device-compliance
description: Enforce on-device and product-compliance boundaries for Meta Wearables iOS DAT, Android DAT, native Display, and Ray-Ban Display Web Apps. Use when designing or reviewing camera, glasses-microphone, audio, sensor, Display, local-first, privacy, permission, thermal, network, background, fallback, or release behavior.
---

# Meta Wearables on-device compliance

Own the claim that a Meta Wearables feature is safe, bounded, and honest about
where data and control actually live. This role covers the phone companion,
glasses transport, native DAT, native Display, and hosted Display Web App; it
does not turn a phone fallback, mock, or browser simulator into glasses-native
behavior.

## Read before acting

- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md), the [full-SDK matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), the [generation matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md), and the [privacy/release route](../../../70-meta-wearables/08-privacy-publishing-and-release.md).
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when companion, firmware, on-glasses DAT-app, release-channel, thermal/power, or recovery state affects the data-flow claim.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) to distinguish Bluetooth/Wi-Fi/HFP/A2DP transport from processing location, queue/storage, and physical evidence.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) for sensor source, permission, raw-data, processing-location, sampling, thermal, teardown, and phone-fallback rules.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) to keep app identity, callbacks, attestation, credentials, Web App origin, and “on-device” processing as separate claims.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) to locate processing, storage, network, raw-media, and fallback boundaries in the actual adapters.
- Inspect the actual iOS target, Android module, or Web App before making a claim: package/artifact revision, deployment target, permissions, privacy manifest/metadata, network destinations, storage, logs, model/runtime path, and fallback.
- Use the [device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md) for source, static, mock, connected, physical, signed, and release evidence.
- Treat the current iOS 0.9.0 and Android 0.9.0 package/changelog as build gates for those releases; do not copy older DAM, lifecycle, minimum-OS, or audio examples into a target without typechecking.

## Compliance workflow

1. Freeze the target profile: consumer label, runtime `DeviceType`/model, platform, exact package/artifact, phone OS, Meta AI version, firmware, requested capability, and evidence level.
2. Draw the data flow from glasses or phone source through local processing, network/vendor services, storage, logs, deletion, and user-visible output. Name every raw frame, photo, audio sample, transcript, sensor reading, Display payload, identifier, diagnostic, and model output.
3. Classify the processing location as `glasses-native`, `phone-local`, `remote`, `mixed`, or `unknown`. Use `on-device confirmed` only when the exact implementation and evidence establish the path; use `local-first` when a documented explicit remote fallback remains.
4. Gate every capture or transmission on capability, permission, consent, purpose, thermal/battery/link state, and lifecycle. Stop or degrade on doff/fold, disconnect, denial, background, thermal, battery, or stale-session events.
5. Apply the platform contract: iOS DAT permissions/configuration and 0.9.0 deployment, Android DAT manifest/artifact/configuration, or Web App HTTPS/600×600/MRBD/input rules. Keep native DAT and Web Apps separate.
6. Define a user-visible fallback for every unavailable operation: phone-local camera/audio, cached data, typed unavailable state, or explicit retry. Never silently substitute a phone microphone for glasses HFP.
7. Run static and deterministic checks, then the named connected/physical task when the account, target, firmware, and hardware exist. Keep source, mock, browser, connected, physical, signed, and production claims separate.
8. Return a compliance report with open gates. Stop before release if the data path, permission, retention, policy, target, or evidence contract is unresolved.

## Fast path

Create a processing ledger for one data item: source, location, retention, network/storage path, consent, thermal impact, and fallback. Classify the claim and test its earliest boundary; do not audit unrelated capabilities before that path is honest.

## Required output

Return:

- target and route profile;
- data-flow table with processing location, network, storage, deletion, and consent;
- permission/configuration and capability-gate table;
- thermal, lifecycle, background, link, and fallback behavior;
- local model/audio/video memory and retention policy;
- source/static/mock/connected/physical evidence status;
- unresolved privacy, account, release, device, generation, and policy gates.

## Claim vocabulary

| Label | Use only when |
| --- | --- |
| `on-device confirmed` | The implementation path and target evidence show that the named processing stays on the named device boundary. |
| `phone-local` | The phone performs the processing; do not describe it as glasses-native or glasses-only. |
| `local-first` | The default is local but an explicit, disclosed remote path exists. |
| `remote-required` | The capability cannot complete without a named network/vendor service. |
| `source-conflict` | Official sources disagree; preserve both observations and gate the feature. |
| `to-verify` | The selected artifact, target, runtime, or physical result is missing. |
| `unsupported` | The selected route or source explicitly does not provide the capability. |

## Hard boundaries

- Never call a phone camera, phone microphone, remote transcription, or Web App browser API a glasses-native capability.
- Never capture raw camera/audio/sensor data silently or retain it by default.
- Never promise background continuation, offline behavior, HFP audio, sensors, Display legibility, or thermal safety from source prose alone.
- Never map “Gen 3,” Meta Glasses, or a retail label to a DAT enum without current official runtime and named-device evidence.
- Never put credentials, personal media, device identifiers, or private diagnostic output into public Web App assets, logs, screenshots, fixtures, or skill archives.
- Never use `on-device` as a marketing synonym for “uses a phone companion.” State the processing boundary plainly.
- Never use Developer Mode, a valid callback, app attestation, or a release
  channel as evidence that data stays on glasses or the phone. Confirm the
  actual processing, network, storage, consent, and retention path separately.

## Related roles

- [Full-SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Camera/audio](../meta-dat-camera-audio/SKILL.md)
- [Transport/reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Native Display](../meta-dat-display/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Privacy/publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)

## Sources

- [On-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [Meta Wearables full reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS repository and changelog](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository and changelog](https://github.com/facebook/meta-wearables-dat-android)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory)
