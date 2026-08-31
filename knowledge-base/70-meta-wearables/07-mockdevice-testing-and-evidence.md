# MockDevice testing and evidence

MockDeviceKit is a development and test surface for DAT integrations. It can
simulate glasses lifecycle, permissions, camera media, photos, and captouch
inputs without physical hardware. It is valuable because it makes state and
failure handling repeatable; it is not a replacement for physical glasses.

## Mock coverage

Use the current `MWDATMockDevice` APIs and the official sample to exercise:

- enable/disable and pair a named `GlassesModel`;
- power, fold/unfold, don/doff, disconnect, and availability transitions;
- granted/denied permission status and request results;
- video feed files and captured-image files;
- synchronous `MockCameraKit.setCameraFeed(cameraFacing:)` setup in the 0.9.0
  route; remove stale async assumptions from fixtures;
- captouch tap/tap-and-hold behavior where the mock exposes it;
- `MockDeviceTestClient` or the test-server route when a UI-test process must
  control the simulated device.

For the full iOS product surface, keep the two process boundaries explicit:
the app process enables `MockDeviceKit` and starts the test server; the
XCUITest process links `MWDATMockDeviceTestClient`, waits for the port file,
drives sanitized actions, and unpairs the device. The [portable test-client
starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift)
type-checks against the selected DAT 0.9.0 product. It does not turn UI-test
control into runtime or physical glasses evidence.

Keep each test's setup and teardown deterministic. Reset the mock and release
listeners after every case so a prior simulated device cannot make a later
test look registered or connected.

The current changelog says MockDevice checks link availability in the same
family as real devices. Missing Bluetooth or Wi-Fi/local-network configuration
should therefore be allowed to fail the mock in the same target-inventory test
as a real integration, rather than being patched around in the fixture. This is
static/mock evidence, not hardware proof.

## Fixture matrix

| Fixture | Useful for | Still missing |
| --- | --- | --- |
| Registration unavailable/denied | Phone UI and retry logic | Meta AI callback and account behavior. |
| Permission denied/allow-once | Permission copy and state reducers | Real companion-app approval. |
| Fold/doff/power-off | Session/stream teardown and recovery | Physical Bluetooth timing and hardware behavior. |
| Thermal/battery/compatibility error | Typed error routing and update actions | Actual thermal/power behavior on the named device. |
| Mock camera/video/photo | Frame/photo pipeline, backpressure, persistence | Camera optics, transport quality, ambient light, and physical capture. |
| Mock captouch/display action | Button state and idempotent command handling | Neural Band/temple gesture recognition and visual legibility. |
| Web App browser simulator | 600x600 layout, D-pad focus, additive-style preview | WebView firmware, EMG, glasses optics, and release delivery. |

## Evidence ladder

Use the strongest label supported by the actual run:

```text
source -> SDK/static -> fixture/mock -> simulator/browser UI
  -> physical/system -> signed/release-channel -> production
```

Do not upgrade a lower level. A MockDevice test can establish that the app
responds to `.paused` or a failed photo capture; it cannot establish that a
real pair enters that state under the same timing. A browser simulator can
establish focus order at 600x600; it cannot establish display legibility or
Neural Band input.

## Test handoff

Every DAT test report should include:

- package/repository revision, Xcode/Swift/iOS target, and test destination;
- model enum and any runtime device metadata;
- registration/permission/compatibility/session/capability setup;
- fixture input files and whether they contain personal media;
- expected state transitions and deterministic assertions;
- evidence level, exact result bundle/log, and the next physical or release
  gate that remains.

## Sources

- [Meta Mock Device Kit overview](https://wearables.developer.meta.com/docs/mock-device-kit)
- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS Camera Access sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess)
- [DAT iOS Display Access sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/DisplayAccess)
- [DAT iOS testing guide](https://wearables.developer.meta.com/docs/testing-mdk-ios)
- [Apple testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)
