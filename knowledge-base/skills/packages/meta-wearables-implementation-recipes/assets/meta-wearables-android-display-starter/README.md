# Meta Wearables Android Display starter

This is a narrow, source-aligned DAT 0.9.0 Kotlin adapter for a selected
Android Display-capable device. It follows the official Android DisplayAccess
shape: `SpecificDeviceSelector` → `Wearables.createSession(...)` →
`DeviceSession.state`/`errors` → `addDisplay()` → `Display.state` →
`sendContent { ... }` → `removeDisplay()` → session stop.

The adapter deliberately keeps registration, runtime permission requests,
`Wearables.initialize(context)`, device metadata/picker policy, and the
Android UI layer outside the reusable coordinator. The caller must select a
connected, compatible device whose `Device.isDisplayCapable()` result is true.

## Compile gate

Copy the Kotlin file into a real Android target with the exact selected Maven
artifacts, normally `com.meta.wearable:mwdat-core:0.9.0` and
`com.meta.wearable:mwdat-display:0.9.0`, plus the target's Kotlin/coroutines and
Android configuration. Resolve GitHub Packages credentials through the
target's private `local.properties`/environment path; never add them here.

The asset has not been compiled in this knowledge-base repository because no
Android target, Android SDK build graph, or authenticated Maven artifact
resolution is present here. Its symbols are anchored to the public 0.9.0
Android DisplayAccess sample and changelog, so the target compile remains an
explicit gate rather than an implied claim.

## Evidence boundary

The adapter's reducer-facing events, epoch checks, bounded snapshot, and
child-before-parent teardown are reusable code evidence. They do not prove
registration, Bluetooth transport, firmware/companion readiness, physical
Display optics, input timing, thermal behavior, Gen 2/Gen 3 compatibility, or
signed/release-channel behavior.

Sources:

- [Android DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess)
- [DAT Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
