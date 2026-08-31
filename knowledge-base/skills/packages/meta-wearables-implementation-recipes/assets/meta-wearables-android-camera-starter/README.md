# Meta Wearables Android camera starter

This is a narrow DAT 0.9.0 Kotlin camera/photo coordinator. It follows the
official Android `CameraAccess` shape: `DeviceSession` → `addCamera()` →
`Camera.stream` → `Flow` collection/photo capture → camera close → session stop.

The coordinator keeps raw `VideoFrame` values inside the adapter. It reports
only the first-frame event and a photo-received event; the caller owns bounded
decoding, retention, deletion, and any network/model decision. Phone
`AudioRecord` is intentionally not part of this adapter and must not be
reported as a glasses microphone capability.

## Compile and evidence gate

Copy the Kotlin file into a real Android target with
`com.meta.wearable:mwdat-core:0.9.0` and
`com.meta.wearable:mwdat-camera:0.9.0`, then resolve the exact Kotlin/coroutine
and Android configuration. The source shape is anchored to the official
`CameraAccess` sample and 0.9.0 changelog, but it is not compiled in this
knowledge-base repository because Android SDK/Gradle/Maven authentication are
not available here.

Run target build/tests before requesting `AND-BUILD-01`, `MOCK-03`, or
`DAT-CAM-01`. A compiled coordinator does not establish transport, optics,
photo quality, firmware, thermal behavior, HFP audio, or Gen 2/Gen 3 support.

## Privacy and lifecycle boundary

- Query/request camera permission explicitly; keep any Meta AI app redirect
  behind an app-owned confirmation surface.
- Cancel `Flow` collectors, close the camera child, and only then stop the
  parent `DeviceSession`.
- Stop on disconnect, stream terminal state, denial, doff/background, error, or
  cancellation and return to the phone fallback.
- Use the separate Android phone-audio route for sound-in-video; this file does
  not infer an undocumented glasses microphone API.

## Official anchors

- [DAT Android `CameraAccess` sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/CameraAccess)
- [DAT Android camera view model](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/CameraAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/cameraaccess/camera/CameraViewModel.kt)
- [DAT Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
