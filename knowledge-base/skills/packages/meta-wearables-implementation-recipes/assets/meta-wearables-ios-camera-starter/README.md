# Meta Wearables iOS camera starter

This is a narrow DAT 0.9.0 iOS camera/photo coordinator. It follows the
official `CameraAccess` shape: `DeviceSession` → consolidated `Camera` →
`Camera.stream` → bounded frame observation/photo capture → camera stop →
session stop.

The adapter keeps raw `VideoFrame` values inside the SDK boundary. It reports a
first-frame event rather than persisting or forwarding raw frames, and sends
captured photo bytes only to the caller-provided phone-local `photoSink`. The
caller owns decoding, consent, retention, and any model/network decision.

## Compile and evidence gate

Add the Swift file to an iOS target linking `MWDATCore` and `MWDATCamera` at
the selected DAT release. Resolve the generated API against the exact SPM
product before adapting it. This asset has not been promoted to a standalone
hardware or physical-glasses claim: source alignment proves the adapter shape,
not camera permission, transport, optics, sustained frame delivery, firmware,
thermal behavior, or Gen 2/Gen 3 support.

This asset was type-checked against the selected target's DAT 0.9.0 simulator
`MWDATCore`/`MWDATCamera` XCFrameworks on 2026-08-22. That compile receipt is
still narrower than a full target build or hardware run; run the selected
target's build/tests before requesting `DAT-CAM-01` or `TRN-STREAM-01`.

## Privacy and lifecycle boundary

- Camera permission checks and Meta AI permission redirects remain explicit.
- The camera is stopped before the parent session; listener tokens are cancelled
  before child teardown.
- Background, doff, disconnect, denial, stream error, queue pressure, and
  capture failure return a typed phone fallback.
- A phone microphone or remote service is not implied by this camera adapter.

## Official anchors

- [DAT iOS `CameraAccess` sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess)
- [DAT iOS camera view model](https://github.com/facebook/meta-wearables-dat-ios/blob/main/samples/CameraAccess/CameraAccess/ViewModels/CameraViewModel.swift)
- [DAT iOS 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
