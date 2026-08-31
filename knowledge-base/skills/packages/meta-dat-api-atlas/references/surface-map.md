# DAT API atlas surface fixture

Use this fixture to judge whether a role response is a real API/source handoff
or a generic wearable prompt.

## Input

“Build an iOS app that registers with Meta AI, streams camera frames, captures a
photo, listens to the glasses microphone, shows a glance card on Ray-Ban
Display, runs without hardware in UI tests, and later supports Gen 2 and Gen 3.”

## Required mapping

1. Pin DAT iOS release/commit and resolve the iOS minimum-OS conflict.
2. Name confirmed package modules versus platform-index names that still need
   package/API verification.
3. Show the lifecycle from configure → registration/callback → permission →
   device/session → camera/display/audio → stop/recovery.
4. Use the current camera/stream/photo route and identify the
   `addCamera` signature as a versioned typecheck gate.
5. Route microphone capture through documented HFP/AVAudioSession behavior and
   require microphone consent, route verification, and physical audio proof.
6. Gate native Display on capability and attach it after a started session; keep
   Web Apps as a separate MRBD-only route.
7. Use MockDeviceKit and its test server for deterministic UI tests, explicitly
   excluding physical camera/audio/display proof.
8. map Gen 2 to the current official device/firmware/version matrix and keep Gen
   3 `to-verify` if no current mapping exists.
9. If the request includes a Web App, compare the full Developer Center index
   with toolkit `main` and keep text composition, offline, back, extended
   gestures, and sensors source-conflicted until target proof closes the gap.
10. Include the App Store/release-channel boundary and the next account/hardware
   gate.

## Rejection conditions

- a “full SDK” claim based only on one module or one marketing page;
- a raw glasses microphone claim without HFP route/consent evidence;
- a Display claim without `supportsDisplay()` and a named physical result;
- a Gen 3 alias invented from `.metaGlasses` or a product announcement;
- a simulator/mock result described as glasses or production proof;
- credentials or personal media embedded in examples.

## Sources

- [Meta Wearables full platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS MockDevice testing](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS Display access](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession)
