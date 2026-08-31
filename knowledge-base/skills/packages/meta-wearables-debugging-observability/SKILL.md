---
name: meta-wearables-debugging-observability
description: Diagnose Meta Wearables DAT iOS and Android setup, registration, permission, device-link, session, camera, audio, Display, and transport failures with source-grounded, read-only evidence. Use when a DAT app cannot communicate with glasses, a stream or Display session fails, live DAT Inspector MCP tools are available, logs need a redacted diagnostic bundle, or a team must separate app bugs from Meta AI companion, firmware, device, and release-channel boundaries.
---

# Meta Wearables debugging and observability

Diagnose the first failing state in a Meta Wearables integration and produce a
small, redacted evidence packet. Treat debugging as an observation workflow,
not permission to mutate the Meta AI app, glasses, account, registration, or
release channel.

## Read before acting

- Read the [debugging and observability route](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md).
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the failure involves a Display action, gesture, sensor watch, permission, stale event, or physical input result.
- Read [DAT iOS foundations](../../../70-meta-wearables/01-dat-ios-sdk-foundations.md)
  or [DAT Android parity](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md)
  for the selected platform, then the relevant [API atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md)
  or [Android API atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md).
- Read [operational readiness](../../../70-meta-wearables/18-operational-readiness-and-recovery.md),
  [transport reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md),
  and [device proof](../../../70-meta-wearables/07-mockdevice-testing-and-evidence.md)
  when firmware, link, audio, thermal, Display, or physical behavior is involved.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when the first failure involves callback/identity configuration, Developer Mode/release attestation, package/signing credentials, or a redacted diagnostic handoff.
- Refresh the official [DAT iOS](https://github.com/facebook/meta-wearables-dat-ios),
  [DAT Android](https://github.com/facebook/meta-wearables-dat-android),
  [DAT MCP](https://mcp.developer.meta.com/wearables), and version-dependency
  sources before using a version-sensitive symbol or current issue claim.

## Procedure

1. **Freeze the target.** Record platform, app target, SDK package/artifact and
   commit/tag, phone OS, app build, exact product wording, runtime device type
   if known, firmware, Meta AI version, mode/channel, and operation being
   attempted. Mark unknown fields `to-verify`.
2. **Separate the evidence plane.** Label each observation as source, config,
   compile, mock, browser-simulator, connected-device, physical, signed, or
   release-channel evidence. Do not use a source, mock, or compile result as
   hardware proof.
3. **Use live MCP evidence first when available.** Discover and connect to the
   local DAT Inspector/debug server. Establish `get_connection_status`,
   `get_sdk_state`, and `get_dat_readiness` before deeper diagnosis; connection
   failure is not the same as SDK or device failure.
4. **Walk the boundary.** Inspect `get_companion_boundary_diagnosis`,
   `get_device_path`, `get_permissions`, and `get_device_properties` when the
   readiness baseline points outside app code. The path is app -> DAT
   registration -> Meta AI permissions -> device selection/link -> session ->
   capability/stream.
5. **Reproduce narrowly.** Ask for one exact operation, then wait for
   `wait_for_events` with the narrowest category/source. Collect `get_errors`
   and `get_event_digest` only as needed. Identify the first failing state and
   later symptoms separately.
6. **Diagnose before editing.** Check initialization/configuration, callback,
   registration, permission, device eligibility, link state, session, stream or
   Display state, audio route, transport, and thermal/power in that order. Use
   the selected platform's typed result/error rather than translating symbols
   across iOS and Android.
7. **Export safely.** Use `export_diagnostic_bundle` when available, inspect
   it for raw frames, audio, tokens, client credentials, URLs with secrets,
   precise device identifiers, and personal data, then redact before handoff.
8. **Return a bounded conclusion.** Name the evidence plane, first blocking
   state, observed fact, next developer action, fallback, and proof still
   missing. State when the result is only app-visible boundary diagnosis.

## Platform anchors

| Layer | iOS observation | Android observation |
| --- | --- | --- |
| Initialization | `Wearables.configure()` and configuration logs | `Wearables.initialize(context)` and initialization logs |
| Registration | `registrationState`, callback handling, `startRegistration()` | `Wearables.registrationState`, Activity/deeplink callback, registration result |
| Device | `devices`, selectors, `device.compatibility`, `device.properties`, `device.linkState` | `Wearables.devices`, selectors, compatibility/properties/link state |
| Permissions | DAT permission and companion-boundary evidence | `checkPermissionStatus(...)` plus companion-boundary evidence |
| Session/capability | `DeviceSession`/session state, errors, camera or Display state | `Session`/`DeviceSession`, `DatResult`, state, camera or Display result |
| Live evidence | iOS DAT Inspector events and SDK logs | Android DAT Inspector events and SDK logs |

Use the exact resolved artifact and API reference for the target. The table is
a routing aid, not proof that the platform symbols are interchangeable.

## Redaction rules

- Keep state names, timestamps, SDK/artifact revision, app build, capability,
  error category, counts, and recovery result when needed for diagnosis.
- Remove credentials, client tokens, access tokens, raw image/video/audio,
  transcripts, personal data, precise device IDs, account emails, and private
  diagnostic payloads. Replace identifiers with stable local labels such as
  `device-A`.
- Do not log every frame or audio buffer. Prefer counters, durations, codec,
  dimensions, route category, and bounded error digests.
- A redacted bundle is still app-visible evidence; it does not prove physical
  glasses rendering, audio, input, firmware recovery, or public publishing.

## Fast path

Build a first-failure timeline from one run: target tuple -> last known state -> first error -> owning boundary -> next recovery. Capture only redacted structured fields and stop collection once the earliest actionable boundary is identified; do not gather a full diagnostic dump by default.

## Hard boundaries

- Do not mutate Meta AI, glasses, account, permission, registration, project,
  release channel, or tester state during diagnosis unless the user separately
  authorizes that operation.
- Do not diagnose from a single generic “not connected” message when the first
  failing state can be observed.
- Do not map “Gen 3” to a model enum or claim Display/audio/transport support
  from a neighboring device.
- Do not call a local debug-server result companion-app introspection; it is
  evidence exposed through the app/DAT boundary.
- Keep phone fallback and user-visible recovery available when the wearable is
  absent, denied, unsupported, disconnected, or thermally unavailable.

## Required handoff

Return:

- frozen compatibility tuple and selected operation;
- evidence plane and source/package revision;
- baseline readiness and first failing state;
- narrow event/error digest and redaction status;
- likely owner: app, SDK/config, Meta AI boundary, device/firmware, transport,
  audio, thermal/power, or release channel;
- next action, fallback, and exact proof still required.

## Related roles

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Transport reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)

## Sources

- [Official DAT iOS debugging skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/debugging/SKILL.md)
- [Official DAT iOS live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/live-debugging-mcp/SKILL.md)
- [Official DAT Android debugging skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/debugging/SKILL.md)
- [Official DAT Android live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/live-debugging-mcp/SKILL.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Meta device and release evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
