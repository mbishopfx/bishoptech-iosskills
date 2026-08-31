# Meta Wearables Android MockDevice starter

This is a source-aligned DAT 0.9.0 Android fixture harness around
`mwdat-mockdevice`. It keeps MockDeviceKit setup in one target-owned object so
instrumentation tests can exercise registration configuration, Ray-Ban Meta
pairing, lifecycle transitions, camera permission outcomes, file or
phone-camera feeds, captured photos, and captouch input without putting SDK
objects in shared product state.

## Compile and evidence gate

Add `mwdat-mockdevice:0.9.0` to the selected Android target and include
`MetaWearablesAndroidMockDeviceStarter.kt`. Resolve the exact generated API in
the target before adapting it. This asset follows the official Android
`CameraAccess` MockDevice sample and is source-aligned, but it was not compiled
on this host because the workspace has no Android SDK/Gradle/Maven toolchain
receipt.

The fixture is not physical-glasses proof. It cannot establish Bluetooth or
Wi-Fi timing, camera optics, HFP/A2DP audio, Display legibility, Neural Band
behavior, firmware support, thermal/battery behavior, a named Gen 2 pair,
unresolved Gen 3 compatibility, or release-channel behavior.

## Fixture rules

- Call `enable` and pair the simulated `GlassesModel.RAYBAN_META` device in
  instrumentation setup.
- Use `setCameraPermission` to control both status checks and permission-request
  outcomes; do not rely on a default grant when testing denial.
- Use H.265/HEVC-compatible video and JPEG/PNG image fixtures for file-backed
  camera behavior. Android does not transcode mock video automatically.
- Runtime permission grants belong in the instrumentation test target. The
  reusable harness does not issue shell commands or grant permissions itself.
- Stop app-owned camera/session resources in the test, then call
  `unpairRayBanMeta` or `disable` in teardown.
- Keep event assertions to sanitized state/counts. Do not log URIs, media,
  device identifiers, or credentials.

## Official anchors

- [DAT Android MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/mockdevice-testing/SKILL.md)
- [DAT Android CameraAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/CameraAccess)
- [DAT Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
