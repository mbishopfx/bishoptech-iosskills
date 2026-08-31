# Meta Wearables vertical-slice playbooks

Use these playbooks after the [source-pinned API register](../../meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
has been filtered for the selected journey. They turn the team’s route and
evidence contracts into implementation-ready handoffs without pretending that
source rows compile or that a simulator proves glasses behavior.

## Common handoff fields

Every slice should freeze these fields before implementation:

| Field | Required value |
| --- | --- |
| `outcome` | One user-visible result, not a list of SDK features |
| `primary_surface` | Native DAT, native Display, Web App, or phone |
| `fallback_surface` | The useful experience when the primary route is absent or fails |
| `target_tuple` | App target, OS/min SDK, package/artifact, runtime model, phone, companion, firmware, and channel when known |
| `api_rows` | Exact `IOS-*`, `AND-*`, `WEB-*`, and compatibility/evidence IDs used |
| `data_path` | `glasses-native`, `phone-local`, `remote`, `mixed`, or `unknown` per data type |
| `owner` | One coordinator/capability owner for registration, session, media, Display, or Web App state |
| `proof` | Source, static, build, mock, browser-sim, connected, physical, signed, release-channel, or production |
| `open_gates` | Missing artifact/API, account, target, firmware, physical, privacy, or release proof |

The selected API row’s status and gate remain attached to the handoff. Do not
replace an unresolved row with a similarly named Swift, Kotlin, browser, or
consumer-product concept.

## Playbook A — Native Display glance card

### Use when

The user needs a compact result and one or two actions on display-capable
glasses, with the phone handling setup, consent, detailed content, and fallback.

### Route

| Platform | Primary adapter | Phone fallback | Minimum source rows |
| --- | --- | --- | --- |
| iOS | DAT registration → `DeviceSession` → native Display | SwiftUI card/detail flow | `IOS-REG-001`, `IOS-PERM-001`, `IOS-DEVICE-001`, `IOS-SESSION-001`, `IOS-DISPLAY-001` |
| Android | DAT registration → selected session API → `mwdat-display` | Compose/View card/detail flow | `AND-CORE-001`, `AND-DEVICE-001`, `AND-SESSION-001`, `AND-DISPLAY-001` |
| Gen 2/Gen 3 wording | Never select by label alone | Phone-only until runtime tuple is known | `COMP-TUPLE-01`, `COMP-GEN3-01`, `GEN-STATIC-01` |

### State and ownership

```text
phoneSetup
  -> registrationRequired | permissionRequired | deviceSelectionRequired
  -> sessionStarting
  -> displayStarting
  -> displayActive
  -> focusedAction | dismissed | timeout
  -> displayStopping -> phoneReady

Any state -> disconnected | unsupported | thermalLimited | failed
  -> cancel display/session work -> phoneFallback
```

- The coordinator owns the session epoch and one Display capability.
- The presenter emits a sanitized, short root view; it does not import DAT or
  own lifecycle tokens.
- Gate on the runtime Display predicate (`supportsDisplay()` or the exact
  Android equivalent) before starting the capability.
- Treat focus, action, timeout, clear, stop, disconnect, and stale events as
  separate reducer events.
- Keep raw camera/audio/sensor data out of the Display payload unless the
  product contract explicitly requires a minimized value.

### Proof ladder

1. Reducer/fake: duplicate action, stale epoch, timeout, unsupported, stop.
2. MockDevice: registration, permissions, Display tree/action, disconnect.
3. Target build: exact package/artifact, privacy/configuration, and symbols.
4. Physical: named model, firmware, companion, app/build/channel, legibility,
   input, clear/exit, disconnect, and phone fallback.

A mock or browser preview can validate the state machine and content shape; it
cannot prove optics, brightness, physical input timing, link behavior, or
firmware support.

## Playbook B — Camera/photo to phone-local result

### Use when

The glasses camera supplies a bounded preview or photo, while processing and
storage intentionally remain on the phone. This is a phone-local contract, not
an “on-glasses” claim.

### Route and rows

| Concern | iOS | Android | Required boundary |
| --- | --- | --- | --- |
| Camera ownership | `IOS-SESSION-001`, `IOS-CAMERA-001` | `AND-SESSION-001`, `AND-CAMERA-001` | Camera owns stream/resource; stop child before session. |
| Media/photo | `IOS-MEDIA-001` | Camera/photo symbols from `AND-CAMERA-001` | Bound frames, conversion, photo retention, and deletion. |
| Processing | Phone-local model/algorithm | Phone-local model/algorithm | Declare no remote upload unless separately approved and consented. |
| Fallback | Phone camera/manual input | Phone camera/manual input | Preserve the user outcome without glasses. |

### State and data contract

```text
ready -> sessionStarting -> cameraStarting -> previewing
previewing -> photoCapturing -> processingPhoneLocal -> result
previewing -> backgrounded | doffed | disconnected | thermalLimited | failed
  -> stop camera -> release session -> phoneCameraOrManualFallback
```

- Use a bounded frame policy: drop/coalesce when preview is enough; never grow
  an unbounded queue to preserve every frame by accident.
- Cancel conversion/model work on camera stop and reject frames from old epochs.
- Keep raw frames/photos in memory only as long as the user outcome requires;
  make persistence, export, network, and deletion explicit.
- Do not call `VideoFrame.makeUIImage()`, `AudioRecord`, a mock feed, or a phone
  camera feed physical glasses evidence.
- Record resolution, frame rate, codec, observed dimensions, latency category,
  thermal/battery state, and the fallback result in the evidence packet.

### Proof ladder

- Build/static: package graph, privacy strings/manifest, bounded queue, stop
  path, and processing-location declaration.
- Mock: phone/file feed, denial, stop, doff/fold, disconnect, photo failure.
- Connected/physical: named camera operation, observed stream/photo result,
  tuple, retention/deletion behavior, and recovery.

Use `DAT-CAM-01`, `TRN-STREAM-01`, `ODC-STATIC-01`, `ODC-PHYS-01`, and the
platform-specific `AND-*`/`IOS-*` rows; keep `physical` separate from
phone-local processing proof.

## Playbook C — Audio-first path for non-Display or uncertain Gen 2

### Use when

The experience should work on glasses without assuming a Display, or when a
Gen 2/product label does not establish Display capability. Audio routes are
platform-specific and must not be hidden behind a common fake microphone API.

### Route and rows

| Platform | Source route | Fallback | Rows |
| --- | --- | --- | --- |
| iOS | A2DP/HFP through the selected DAT route plus `AVAudioSession` | Phone microphone, playback, or manual input | `IOS-AUDIO-001`, `TRN-AUDIO-01`, `ODC-PHYS-01` |
| Android | Exact artifact route if exposed; keep CameraAccess `AudioRecord` labeled phone microphone | Phone microphone/manual input | `AND-AUDIO-001`, `TRN-AUDIO-01`, `AND-PHYS-01` |
| Any “Gen 3” target | No automatic mapping | Phone/audio fallback until official mapping and tuple | `COMP-GEN3-01`, `COMP-TUPLE-01` |

### Audio state rules

```text
phoneConsent -> routeNegotiating -> routeVerified -> playbackOrCapture
routeNegotiating -> denied | unavailable | interrupted | disconnected
  -> restorePreviousPhoneRoute -> phoneAudioFallback
```

- Ask for and disclose microphone use before capture; verify the actual active
  route and restore the prior route on stop.
- Name direction separately: A2DP output, HFP bidirectional, phone mic, and
  remote transcription are not interchangeable.
- Bound audio buffers, stop taps/collectors on cancellation, and do not log raw
  audio or transcripts by default.
- Treat a connected link, source note, or Android phone `AudioRecord` sample as
  insufficient for physical glasses microphone proof.

## Playbook D — Ray-Ban Display Web App

### Use when

The product is deliberately a hosted HTML/CSS/JavaScript experience delivered
to Meta Ray-Ban Display, not a native DAT module.

### Route and rows

Load `WEB-RUNTIME-001`, `WEB-INPUT-001`, `WEB-SIM-001`, `WEB-NET-001`, and
`WEB-PHYSICAL-001`. Load `WEB-CONFLICT-001` only for its individual feature
tests; do not treat all toolkit capabilities as one supported bundle.

```text
phoneDevelops -> publicHttpsRevision -> browserSimulator
  -> MetaAIAddLaunch -> displayLoaded -> focusedAction -> exit

Any state -> networkUnavailable | unsupportedHost | timeout | staleRevision
  -> phoneFallback
```

- Keep the experience within the 600×600 additive surface, short text, high
  contrast, focusable controls, and D-pad/EMG action model.
- A public HTTPS URL and QR/add flow establish hosted delivery setup, not
  physical legibility, input, firmware, or release proof.
- Test text composition, offline/cache, Escape/back, extended gestures,
  motion/orientation, and geolocation independently because the full reference
  and toolkit currently conflict.
- Declare network destinations, storage/cache, retention, origin, and fallback;
  do not embed private tokens in browser code or URLs.

### Proof ladder

1. Browser simulator: viewport, focus, input, loading/error/exit, performance.
2. Hosted URL: HTTPS, revision, add/launch metadata, network/storage behavior.
3. Physical MRBD: named device/firmware/companion, legibility, input, exit,
   source-conflicted feature results, and fallback.
4. Release: exact hosted revision/channel and repeat of the critical task.

## Playbook E — One outcome across iOS, Android, native Display, and Web Apps

### Use when

The product has one domain outcome but multiple delivery surfaces. Share the
policy and state vocabulary, not the SDK symbols.

### Adapter map

| Shared concept | iOS | Android | Native Display | Web App | Phone |
| --- | --- | --- | --- | --- | --- |
| Registration/setup | DAT URL/callback adapter | DAT activity/callback adapter | Phone-owned | Meta AI add/launch | Native setup |
| Capability selection | Device/Display predicate | Device/Display predicate | Runtime gate | Host/runtime availability | Always available where possible |
| Session/epoch | `DeviceSession` streams | Session API + `Flow`/`DatResult` | Capability owner | Page epoch/host exit | Local task epoch |
| Presentation | SwiftUI | Compose/View | Sanitized root Display tree | 600×600 DOM | Detailed/native fallback |
| Failure | typed adapter event | typed `DatResult`/Flow event | clear/stop/phone | timeout/network/exit | Manual/offline result |

The shared reducer should consume product events such as
`registrationChanged`, `deviceSnapshotChanged`, `capabilityStateChanged`,
`displayActionReceived`, `operationFailed`, and `fallbackRequested`. It should
not consume `MWDAT*`, Kotlin classes, browser `Event`, raw frames, or raw audio.

### Cross-surface acceptance

- Every route has one owner, one epoch, one stop path, and one fallback.
- The same user outcome is possible on the phone without glasses.
- Capability differences are visible as typed state, not hidden parity claims.
- `Gen 2` and `Gen 3` are tested as named tuples; neither is inferred from a
  consumer label or enum.
- Source, build, mock/browser, connected, physical, signed, and release results
  are recorded separately per surface.

## Implementation handoff

Return this compact packet to the team lead:

```text
playbook: A | B | C | D | E
outcome: <one sentence>
primary_surface: <route>
fallback_surface: <route>
target_tuple: <app/OS/artifact/runtime/phone/companion/firmware/channel>
api_rows: <row IDs>
data_path: <classification per data type>
state_owner: <coordinator/capability owner>
proof_completed: <evidence levels and exact task>
open_gates: <missing source/build/account/device/privacy/release proof>
```

Do not return `full SDK`, `on-device`, `Gen 3 supported`, or `physical glasses
works` unless the packet contains the evidence required by that claim.

## Sources

- [Meta Wearables application architecture route](../../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md)
- [Source-pinned API surface manifest](../../meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Device and release evidence packet](../../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
- [On-device compliance and runtime contract](../../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
