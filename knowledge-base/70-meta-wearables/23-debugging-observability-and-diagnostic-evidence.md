# Debugging, observability, and diagnostic evidence

This route turns a Meta Wearables failure into a bounded, source-grounded
diagnosis. It covers the official DAT iOS and Android debugging roles and their
optional local DAT Inspector/live-debugging MCP counterpart. It does not grant
permission to mutate Meta AI, glasses, account, project, registration, or
release-channel state.

## Scope and evidence boundary

Use this route for failures in:

- initialization, configuration, callbacks, registration, and DAT permissions;
- device discovery, selectors, compatibility, link state, and companion
  boundary behavior;
- session creation/start/stop, camera streams/photos, HFP/A2DP audio, native
  Display, transport, and thermal/power behavior;
- Web App launch only when the failure crosses into the native DAT/companion or
  physical Display boundary.

The first-party debugging skills describe app-visible diagnosis through DAT
events and logs. A debug-server result is not Meta AI internal introspection and
does not by itself prove a physical device, firmware, audio, Display, input, or
release result.

## First-failure graph

```text
debug-server connection
  -> SDK readiness
  -> registration/callback
  -> DAT/companion permission
  -> eligible device/compatibility
  -> device link
  -> session
  -> camera/audio/Display capability
  -> stream or payload
  -> recovery/fallback
```

Do not replace the first failed transition with a later symptom. For example,
an empty device list is earlier than a camera error, and a failed debug-server
connection is different from a DAT readiness failure.

## Read-only MCP procedure

When a local DAT Inspector/debug server is available, use this exact sequence:

1. Discover and connect with `discover_debug_servers` and
   `connect_to_debug_server`.
2. Establish the baseline with `get_connection_status`, `get_sdk_state`, and
   `get_dat_readiness`. Always keep connection status separate from SDK and
   device readiness.
3. Inspect `get_companion_boundary_diagnosis`, `get_device_path`,
   `get_permissions`, and `get_device_properties` when the baseline indicates
   registration, permission, device, compatibility, or link trouble.
4. Ask for one narrow reproduction. Use `wait_for_events` with the narrowest
   relevant category/source, then use `get_errors` or `get_event_digest`.
5. Export with `export_diagnostic_bundle` only when a handoff needs it. Inspect
   and redact before storing or sharing.

Do not poll every event, mutate state, or export unbounded raw media. If the
local server is unavailable, record `DBG-CONN-01` as `not-run` and fall back to
app logs, source/config inspection, MockDevice, connected-device, or physical
evidence at the appropriate level.

## Platform diagnosis map

| Boundary | iOS signal | Android signal | Next owner |
| --- | --- | --- | --- |
| Initialization | `Wearables.configure()` and configuration logs | `Wearables.initialize(context)` and initialization logs | target/configuration |
| Callback/registration | URL callback, `startRegistration()`, `registrationState` | Activity/deeplink callback, `registrationState`, registration result | integration/companion |
| Device eligibility | `devices`, selector, compatibility, properties, link state | `Wearables.devices`, selector, compatibility, properties, link state | device/companion |
| Permission | DAT permission plus companion-boundary diagnosis | `checkPermissionStatus(...)` plus companion-boundary diagnosis | permission/privacy |
| Session | `DeviceSession`/session state and typed errors | `Session`/`DeviceSession` state and `DatResult` | platform integration |
| Camera | camera/stream state, frame counters, stream errors | `addCamera`, `camera.stream.start()`, state, `DatResult` | camera/transport |
| Display | Display state, payload/input callbacks, link lease | Display builder/result, tap/click callbacks, link lease | Display/physical proof |
| Audio/transport | AVAudioSession route plus HFP/A2DP and transport evidence | Android audio/transport observation; do not infer from iOS | audio/transport |

Resolve symbols against the selected package/artifact and API reference. The
table is a diagnostic map, not a cross-platform API contract.

## Diagnosis patterns

| First failure | Inspect | Do not conclude |
| --- | --- | --- |
| Debug server cannot connect | server discovery, app build, debug configuration | DAT or glasses are broken |
| SDK readiness blocked | initialization, target configuration, SDK logs | account or firmware is the first cause |
| Registration/callback blocked | URL/deeplink, Meta App ID, Developer Mode/release mode, companion state, network | device camera or Display is unavailable |
| No eligible device | device list, selector, compatibility, link state, firmware/companion versions | camera code is wrong |
| Permission blocked | DAT permission, companion boundary, user-facing denial/recovery | iOS system permission equals DAT permission |
| Session fails | session result/state, selected device, update-required state | stream backpressure is the cause |
| Stream or Display fails after session | capability permission, state, payload/error, link/transport, thermal/power | a neighboring model or “Gen 3” supports it |
| Audio route fails | actual AVAudioSession/Android route, HFP/A2DP, interruption, physical task | phone microphone proves glasses microphone |

## Redacted diagnostic bundle

Keep enough metadata to reproduce the diagnosis without retaining sensitive
content:

- evidence plane, operation, timestamp, platform, package/artifact revision,
  app build, phone OS, product label, runtime type, firmware, companion
  version, and mode/channel;
- connection, readiness, registration, permission, device, link, session,
  capability, and stream/audio/display states;
- first failing state, typed error category, bounded event digest, counters,
  duration, codec/dimensions, route category, and attempted/observed recovery;
- owner hypothesis, next action, fallback, and proof still missing.

Remove tokens, client credentials, account emails, raw images/video/audio,
transcripts, personal data, precise device identifiers, private URLs, and
unbounded logs. Replace a device identifier with a local label such as
`device-A`. A redacted bundle must still identify what it cannot prove.

## Evidence packet rows

| ID | Evidence task | Minimum record | Result boundary |
| --- | --- | --- | --- |
| `DBG-SOURCE-01` | Refresh official iOS/Android debugging and live-MCP roles | URL, revision, retrieval date | Source procedure only |
| `DBG-CONN-01` | Discover/connect to local DAT Inspector | connection status, app/build label | Debug-server connection only |
| `DBG-READINESS-01` | Establish SDK/DAT readiness baseline | SDK state, DAT readiness, first blocker | App-visible readiness only |
| `DBG-BOUNDARY-01` | Inspect companion/permission boundary | diagnosis, permission state, redacted details | No mutation or internal companion proof |
| `DBG-PATH-01` | Trace app-to-capability path | device path, link, session, capability states | Selected target only |
| `DBG-EVENT-01` | Reproduce one failure narrowly | event/error digest and first failure | One operation/build only |
| `DBG-BUNDLE-01` | Export a diagnostic bundle | export status and redaction review | Handoff artifact, not physical proof |
| `DBG-REDACTION-01` | Verify privacy-safe handoff | removed fields and stable-label policy | Does not replace privacy/legal review |
| `DBG-PHYSICAL-01` | Correlate diagnosis with named hardware | device, firmware, task, physical result | Exact pair/build only |
| `DBG-RELEASE-01` | Correlate with signed/channel build | project/version/channel/tester/build result | Not general production proof |

Use [the diagnostic contract](../skills/packages/meta-wearables-debugging-observability/references/diagnostic-contract.md)
for the observation-row schema and handoff template. Use the [device and
release evidence packet](12-device-and-release-evidence-packet.md) for the
cross-role run identity and release gates.

## Sources

- [Official DAT iOS debugging skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/debugging/SKILL.md)
- [Official DAT iOS live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/live-debugging-mcp/SKILL.md)
- [Official DAT Android debugging skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/debugging/SKILL.md)
- [Official DAT Android live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/live-debugging-mcp/SKILL.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Operational readiness and recovery](18-operational-readiness-and-recovery.md)
- [Transport, audio, and runtime reliability](22-transport-audio-and-runtime-reliability.md)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
