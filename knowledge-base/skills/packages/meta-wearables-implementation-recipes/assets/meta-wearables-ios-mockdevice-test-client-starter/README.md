# Meta Wearables iOS MockDevice test-client starter

This is a narrow DAT 0.9.0 UI-test-process boundary around the test-only
`MWDATMockDeviceTestClient` product. The app process starts the official
MockDeviceKit test server; the XCUITest process uses this harness to wait for
the server, pair a simulated Ray-Ban Meta device, drive lifecycle/captouch and
camera fixtures, inspect sanitized state counts, and unpair during teardown.

## Compile and evidence gate

Add the Swift file to the UI-test target and link `MWDATCore` plus
`MWDATMockDeviceTestClient` from the selected DAT release. The harness was
type-checked against the selected DAT 0.9.0 simulator XCFramework interfaces
on 2026-08-22.

The test client is test-process control only. It does not prove registration,
Bluetooth/Wi-Fi timing, camera optics, HFP/A2DP audio, Display legibility,
Neural Band behavior, firmware support, thermal/battery behavior, Gen 2
compatibility, unresolved Gen 3 mapping, signing, or release behavior.

## Process boundary

- App process: enable MockDeviceKit with `initiallyRegistered` as required and
  call `startTestServer(portFilePath:)` during UI-test launch.
- UI-test process: construct `MockDeviceTestClient(portFilePath:)`, wait for
  the server, drive only sanitized actions, and unpair in teardown.
- Pass test-bundle resource names/extensions for media fixtures; never pass or
  log personal media, raw URLs, serials, tokens, or server payloads.
- Keep the local-network permission prompt, test-server port file, and test
  target configuration in the target-owned test setup, not in shared product
  state or this portable asset.

## Official anchors

- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS CameraAccess UI tests](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess/CameraAccessUITests)
- [DAT iOS 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
