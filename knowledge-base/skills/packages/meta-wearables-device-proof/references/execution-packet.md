# Portable Meta Wearables execution packet

Use this reference to record evidence without turning a mock, simulator, or
source lookup into a physical-glasses or release claim.

## Run record

Create a sanitized run directory such as
`artifacts/meta-wearables/mwdat-20260822-ios-rb-display-build42/` with:

```text
manifest.md
static/target-inventory.txt
build/<bundle-id>-<version>-<build>.xcarchive
logs/<task-id>.redacted.log
screenshots/<task-id>-<step>.png
results/<task-id>.md
```

Every result records:

```text
Task ID / status:
Route: native-DAT | native-Display | Web-App | phone-fallback
Source/package revision:
Target/scheme and bundle ID/version/build:
iOS/phone:
Product/model, runtime DeviceType, firmware, DAT-on-glasses version:
Meta AI version and account/channel condition:
Operation exercised / observed result:
Artifacts / negative cases:
What this proves / does not prove:
Next gate:
```

Allowed statuses are `source`, `static`, `build`, `mock`, `browser-sim`,
`connected`, `physical`, `signed`, `release-channel`, `production`,
`not-run`, `blocked`, and `to-verify`.

## Stable task IDs

| Task IDs | Exercise |
| --- | --- |
| `SRC-01`, `CFG-01`, `BUILD-01` | Freeze source/package revision; inspect products, target, callback, permissions, entitlements, privacy manifest, and compile against the selected revision. |
| `MOCK-01`–`MOCK-03` | Mock registration/permission, lifecycle/reconnect, camera/photo stop, unsupported Display, actions, and deterministic assertions. |
| `WEB-SIM-01` | Browser simulator load, 600×600 layout, focus, arrow/Enter input, additive preview, loading, timeout, and error; keep toolkit-described text composer, offline cache, Escape/back, sensors, and extended gestures as separate `to-verify` rows because the public index conflicts with toolkit `main`. |
| `DAT-REG-01`, `DAT-SES-01` | Meta AI registration callback, cold/warm return, denial/cancel, named-device selection, compatibility, session, pause/stop/reconnect. |
| `DAT-CAM-01`, `DAT-AUD-01` | Physical camera/photo lifecycle and documented HFP/A2DP audio route, including stop and route restoration. |
| `DAT-DISP-01`, `WEB-PHYS-01` | Native Display capability/focus/action/clear/disconnect and physical MRBD Web App launch/input/error/exit; source-conflicted Web App features require separate closure rows. |
| `REC-01` | Missing glasses, denied permission, Bluetooth/Wi-Fi/local-network denial, stale session, timeout, low power/thermal, and companion termination. |
| `REL-01`, `PROD-01` | Signed identity/entitlements/channel delivery, then live production operation only after prior gates pass. |

## Hard proof rules

- Record the exact product/model, runtime `DeviceType`, firmware, phone OS,
  Meta AI version, DAT package revision, build identity, and operation.
- Gen 2 evidence never proves another generation. Keep “Gen 3” `to-verify` until
  current official mapping and named-device evidence exist.
- A mock or browser-simulator pass proves controlled logic only. A connected
  result is limited to that named pair. Only the exact physical script proves
  glasses camera, HFP audio, Display, Neural Band/temple input, optics, or
  comfort for that pair.
- A signed archive does not prove Meta release-channel delivery, App Store
  approval, or production behavior.
- The public Web Apps index and toolkit `main` currently conflict about text
  composition, offline, back, extended gestures, and sensors. Preserve both
  source revisions and keep a phone/manual/online fallback until target proof
  closes each feature.
- Redact tokens, callback query values, serials, MAC/device identifiers, email,
  raw photos/video/audio, transcripts, and private Display content. Store
  counts, dimensions, sample rates, error categories, hashes, and sanitized
  screenshots instead.

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta DAT iOS MockDevice testing](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Apple running apps on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Apple testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
