---
name: meta-wearables-transport-reliability
description: Design and review Meta Wearables DAT transport and runtime reliability across Bluetooth, Wi-Fi/local network, HFP/A2DP audio, camera and Display backpressure, background, thermal/power, disconnect, and recovery paths on iOS and Android. Use for Wi-Fi streaming, local-network configuration, audio-route failures, link instability, latency, dropped frames, transport parity, or reliability claims.
---

# Meta Wearables transport and reliability

Own the transport contract between the iOS/Android companion, Meta AI, and
the glasses. Keep Bluetooth control/registration, Wi-Fi media transport,
HFP/A2DP audio, local-network configuration, application processing, and
physical evidence as separate claims.

## Read before acting

- Read the [transport, audio, and reliability route](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md), [session/camera/audio route](../../../70-meta-wearables/03-device-session-camera-and-audio.md), [Android parity route](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md), and [operational-readiness route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md).
- Read the [on-device compliance contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md), [application architecture route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md), [device-proof packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md), and [transport contract reference](references/transport-contract.md).
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when input/sensor event timing, stale callbacks, listener teardown, sampling, or physical gesture recovery depends on transport state.
- Read the [debugging and observability route](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when a transport or audio symptom needs first-failure events, app-visible readiness, or a redacted handoff.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when transport setup includes project identity, callback configuration, package access, signed release, or processing-location evidence.
- Refresh the pinned [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), [full DAT reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat), and [Wearables MCP](https://mcp.developer.meta.com/wearables).
- Inspect the actual target configuration before changing it: iOS `Info.plist`/entitlements and `AVAudioSession`; Android Manifest, runtime permissions, Gradle artifact, and audio route. Never copy a neighboring platform's transport keys.

## Workflow

1. Freeze the tuple: platform, app build, DAT package/artifact, Meta AI app,
   glasses model/runtime identity, firmware/DAT-app, account/mode/channel, and
   requested capability.
2. Classify each hop as Bluetooth control/registration, Wi-Fi/local-network
   media, HFP input, A2DP output, Internet/remote service, or unknown. Record
   the actual observed route rather than inferring it from a connected-device
   label.
3. Audit configuration. On iOS, inspect Bluetooth usage/background keys,
   local-network disclosure, Bonjour services, callback, and selected DAT
   version. On Android, inspect Bluetooth/Internet permissions, callback,
   application/client metadata, target SDK, and the resolved Maven artifact;
   keep the reviewed Android Wi-Fi parity question explicit if the artifact or
   docs do not establish it.
4. Define resource ownership and bounded queues for camera, Display, and
   audio. Specify drop/coalesce/block policy, timestamps, stop order,
   cancellation, route changes, and what happens when the link degrades.
5. Treat HFP and A2DP as separate audio paths. Verify route settlement,
   consent, sample format, interruption, output selection, and restoration;
   do not call a phone microphone or A2DP playback a glasses microphone.
6. Handle typed lifecycle, battery, thermal, peak-power, doff/fold, timeout,
   and disconnect states with a visible fallback and bounded recovery. Avoid
   blind retry loops and never retry a thermal or power shutdown automatically.
7. Classify processing location separately from transport. Wi-Fi or Bluetooth
   does not prove glasses-native inference, and a local phone consumer does not
   prove remote processing is absent.
8. Return source/static/compile/mock/connected/physical/signed evidence with
   the exact transport, route, processing, and failure fields.

## Fast path

Choose one bounded operation and write its states: start -> active -> degraded or disconnected -> recover or stop. Measure queue, latency, and thermal budgets at the adapter boundary, test interruption/reconnect, and defer other transports.

## Required output

- transport and processing-location diagram;
- iOS/Android configuration and parity matrix;
- audio-route matrix for phone mic, HFP input, A2DP output, and remote speech;
- queue/backpressure, cancellation, thermal, battery, and stop-order policy;
- failure/recovery table with the first failing state and typed fallback;
- redacted test script for mock, build, connected, and physical runs;
- explicit status for Wi-Fi parity, “Gen 3,” and any source-conflicted route.

## Hard boundaries

- Never infer Wi-Fi support on Android from iOS configuration or a broad
  `INTERNET` permission; resolve the artifact/docs and test the named target.
- Never treat Bluetooth connection, registration, or a stable link as proof of
  camera, Display, HFP, Wi-Fi, or physical input capability.
- Never claim on-device processing from a transport path. Record where raw
  frames/audio, inference, storage, and network transfer occur.
- Never persist raw personal media or device identifiers in logs, fixtures,
  screenshots, diagnostics, or skill archives.
- Never hide link, permission, timeout, thermal, or power failure behind an
  indefinite spinner or unbounded automatic retry.
- Never use a mock, browser simulator, phone-only audio route, or one device
  generation as evidence for another generation or for release readiness.

## Related roles

- [DAT camera and audio](../meta-dat-camera-audio/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Android API atlas](../meta-dat-android-api-atlas/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
- [Apple local network privacy](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription)
- [Apple Network framework](https://developer.apple.com/documentation/network)
- [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions)
