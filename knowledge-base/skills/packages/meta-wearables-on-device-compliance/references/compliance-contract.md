# On-device compliance contract

Use this reference as the working form for the compliance role. It is a
contract for claims and evidence, not a guarantee that a target supports every
listed capability.

## Target profile

```text
consumerLabel:
sdkDeviceType:
platform:
surface: native-dat | native-display | web-app | phone-fallback
packageOrArtifactRevision:
phoneOSAndCompanionVersion:
glassesFirmwareAndDATVersion:
requestedCapabilities:
accountOrReleaseChannel:
evidenceLevel:
```

## Data-flow record

| Field | Required question |
| --- | --- |
| `dataClass` | Is this a frame, photo, audio sample, transcript, sensor value, Display payload, identifier, log, or model output? |
| `source` | Does it originate on glasses, phone, Web App host, or a remote service? |
| `purpose` | What user-visible action requires it? |
| `processingLocation` | `glasses-native`, `phone-local`, `remote`, `mixed`, or `unknown`? |
| `networkDestination` | Is the network unused, optional and explicit, required, or unknown? Name the vendor/endpoint. |
| `storageAndRetention` | Is it held in memory, local storage, logs, vendor storage, or nowhere? For how long? |
| `consentAndNotice` | What permission, user action, notice, and revocation path exist before collection? |
| `fallback` | What happens on denial, disconnect, background, thermal, battery, offline, or unsupported capability? |
| `evidence` | Which source/static/mock/browser/connected/physical/release artifact proves the claim? |

## Capability gates

| Capability | Must verify | Common false claim |
| --- | --- | --- |
| Camera/photo | DAT session, camera ownership, permission, bounded consumer, thermal/battery/link state, stop/doff recovery | A phone-camera MockDevice feed proves glasses optics or physical transport. |
| Glasses microphone/HFP | HFP route, iOS/Android audio configuration, microphone consent, route settlement, 8 kHz/mono behavior, teardown | A phone microphone or A2DP playback proves glasses microphone input. |
| A2DP output | Active output route, interruption, volume/user control, content disclosure, stop behavior | Any connected glasses name guarantees the same audio route. |
| Native Display | `supportsDisplay`/`isDisplayCapable`, started session, render/input/clear/error behavior, physical legibility | A Display-capable frame or browser preview proves a named device can render. |
| Web App | HTTPS URL, MRBD metadata, 600×600 additive layout, focus/input, loading/error/exit, Meta AI add/launch | Localhost or simulator output proves on-glasses delivery. |
| Sensors/geolocation | Exact runtime API, permission, user gesture, offscreen/stop policy, target firmware, fallback | Toolkit prose proves a native DAT sensor API or universal firmware support. |
| Offline/local-first | Cached app/data boundary, stale-data wording, cache invalidation, remote-required actions, deletion | A service worker proves all app features work without network. |

## Evidence status

Use one status per claim:

```text
source: official prose/index only
static: target package/artifact/configuration inspected
mock: deterministic fixture or MockDevice result
browser-sim: Web App simulator result
connected: named pair recognized and state captured
physical: named pair performed the scripted operation
signed/release: exact artifact/channel evidence
production: live user path observed
```

`source`, `static`, `mock`, and `browser-sim` do not close a physical glasses
claim. `connected` does not prove every capability. Record the exact operation,
device identity, firmware, companion version, build, and timestamp.

## Platform guardrails

- iOS DAT: pin the selected package; the 0.9.0 changelog says iOS 17.2, and
  the obsolete `MWDAT.DAMEnabled` key should not be copied into a 0.9.0 target.
  Audit camera/microphone/Bluetooth/local-network/accessory/background/privacy
  configuration against the actual target.
- Android DAT: pin the selected `mwdat-*` artifacts; 0.9.0 uses manifest
  metadata and typed `DatResult`/`Flow` surfaces. Do not copy `DAM_ENABLED` or
  old `Session`/`DeviceSession` examples without resolving the artifact API.
- Display Web Apps: deliver over HTTPS with the MRBD marker and 600×600
  additive layout. Keep text composition, offline, back, extended gestures,
  and sensors source-conflicted until the selected runtime and physical pair
  close them independently.

## Report template

```text
claim:
target:
route:
processingLocation:
networkPolicy:
permissionsAndNotice:
retentionAndDeletion:
thermalLifecycleFallback:
evidence:
status:
openGate:
nextTask:
```

## Sources

- [Meta Wearables full reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Web Apps toolkit agent instructions](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
