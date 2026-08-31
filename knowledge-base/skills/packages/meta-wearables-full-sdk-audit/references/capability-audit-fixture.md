# Full-SDK capability audit fixture

## Input

“Use the full Meta Wearables SDK to build one iOS app for Ray-Ban Meta Gen 2,
Gen 3, and Ray-Ban Display, with camera, glasses microphone, Display UI,
sensors, offline Web Apps, and Android parity.”

## Required result

- separate iOS DAT, Android DAT, native Display, Web Apps, phone audio, and
  Meta AI/account surfaces;
- resolve “regular SDK” through the manifest terminology contract as an
  ambiguous phrase, and treat “full SDK” as a composite audit rather than a
  third package family;
- four runtime DAT modules/artifacts per mobile target, the iOS test-only
  `MWDATMockDeviceTestClient`, and the exact package/artifact revision;
- camera/photo, HFP/A2DP, native Display, sensor, update/health, MockDevice,
  MCP/debug, privacy, and release rows;
- Android phone-microphone recording labeled separately from a glasses
  microphone claim;
- iOS/Android upstream `AGENTS.md` version/DAM/session conflicts preserved;
- Web Apps text/offline/back/gesture/sensor conflict preserved;
- Gen 2 mapped only through current runtime/device/firmware evidence and Gen 3
  left `to-verify` if no public mapping exists;
- consumer product wording, SDK model identity, and runtime capability kept as
  separate fields, including the 2026 “Meta Glasses” product name;
- mock, browser, target build, connected, physical, signed, release-channel,
  and production evidence separated.

## Rejection conditions

- “full SDK” means copying every upstream skill without inspecting the target
  dependency graph;
- a phone microphone, Android sound-in-video sample, or iOS HFP setup is called
  raw glasses microphone access;
- a `Session`/`DeviceSession` name is translated across versions without the
  selected API reference;
- `DAMEnabled`/`DAM_ENABLED` is added as current 0.9 guidance without recording
  the changelog conflict;
- a product-generation label is substituted for a runtime capability;
- a product announcement is treated as a DAT support matrix or `DeviceType`
  mapping;
- source, mock, or simulator output is described as physical or production proof.

## Sources

- [Full capability and source-conflict matrix](../../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](../../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android phone-microphone sample](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/CameraAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/cameraaccess/stream/AudioInputHandler.kt)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/)
- [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
