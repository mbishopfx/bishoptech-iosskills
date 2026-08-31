# Meta Wearables iOS MockDevice starter

This is a narrow DAT 0.9.0 iOS fixture harness around `MWDATMockDevice`. It
keeps MockDeviceKit setup in one target-owned object so tests can exercise
registration configuration, Ray-Ban Meta pairing, lifecycle transitions,
camera permission outcomes, file or phone-camera feeds, captured photos, and
captouch input without putting SDK objects in shared product state.

## Compile and evidence gate

Add `MetaWearablesMockDeviceStarter.swift` to an iOS test or debug target that
links `MWDATCore` and `MWDATMockDevice` at the selected DAT release. This asset
was type-checked against the selected target's DAT 0.9.0 simulator
`MWDATCore`/`MWDATMockDevice` XCFrameworks on 2026-08-22.

The receipt proves only that this fixture boundary matches the selected iOS
package. A MockDevice run does not prove Bluetooth timing, camera optics,
HFP/A2DP audio, Display legibility, Neural Band behavior, firmware support,
thermal/battery behavior, a named Gen 2 pair, unresolved Gen 3 compatibility,
or release-channel behavior.

## Fixture rules

- Call `enable` and pair the simulated `.rayBanMeta` device in test setup.
- Use `setCameraPermission` to control both status checks and permission-request
  outcomes; do not rely on a default grant when testing denial.
- Use HEVC/H.265 video and JPEG/PNG image fixtures when file-backed camera
  behavior is required. Do not put personal media in this package.
- Stop the app-owned camera/session resources in the test, then call
  `unpairRayBanMeta` or `disable` in teardown.
- Keep event assertions to sanitized state/counts. Do not log URLs, media,
  device identifiers, or credentials.

## Official anchors

- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS CameraAccess sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess)
- [DAT iOS 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
