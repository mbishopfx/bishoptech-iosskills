# DAT Android parity and boundaries

This page records the public Android DAT route so the knowledge base covers the
full public mobile SDK family without pretending Kotlin and Swift are one API.
It was refreshed on 2026-08-22 against Android repository `main`
`81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc` and the 0.9.0 release/changelog
dated 2026-08-03.
Use the [Android API surface atlas](20-dat-android-api-surface-atlas.md) for
exact artifact/symbol inventory, 0.9 migration conflicts, and Android-specific
compile gates; this page remains the product-boundary and parity overview.

## Package and target contract

The official Android artifacts are published through GitHub Packages:

| Artifact | Purpose |
| --- | --- |
| `com.meta.wearable:mwdat-core:0.9.0` | Initialization, registration, permissions, device discovery/selectors, and sessions. |
| `com.meta.wearable:mwdat-camera:0.9.0` | Camera/stream capability, frames, and photo capture. |
| `com.meta.wearable:mwdat-display:0.9.0` | Structured Display content, buttons, images, video, and tap/click callbacks. |
| `com.meta.wearable:mwdat-mockdevice:0.9.0` | Mock glasses, permissions, media, lifecycle, and deterministic tests. |

The repository documents Android 10+ and Android Studio/Gradle setup, a GitHub
Packages `read:packages` credential, Bluetooth/Internet permissions, and
Developer Mode for development builds. Use placeholders or environment/local
properties for `APPLICATION_ID`, `CLIENT_TOKEN`, and the package token; do not
commit any real value.

## Lifecycle and typed-result shape

The Android route is conceptually:

```text
Wearables.initialize(context)
  -> startRegistration(activity) / registrationState
  -> devices / permission state
  -> Wearables.createSession(AutoDeviceSelector())
  -> DeviceSession.start()
  -> addCamera() or addDisplay()
  -> capability.start() / Flow or StateFlow observation
  -> stop capability -> stop session
```

Android uses `DatResult<T, E>` for typed success/failure and Kotlin
`Flow`/`StateFlow` for observation. The official 0.9.0 DisplayAccess sample
imports `DeviceSession`, `DeviceSessionState`, and `DeviceSessionError`; some
moving upstream `AGENTS.md`/plugin pages still use the older `Session` wording.
Keep that as a source-conflict/compile gate and check the selected artifact/API
reference before using an exact extension function or enum case.

## 0.9.0 migration inventory

| Change | Implementation consequence |
| --- | --- |
| `DeviceSession.addCamera(streamConfiguration)` returns `Camera`; `Camera.stream`, `Camera.stop()`, and `removeCamera()` own the camera resource | Do not revive direct `addStream()`/`removeStream()` routes; stop the child capability before the session. |
| `FlexBoxScope.buttonGroup` and `ButtonGroupAlignment` | Native Android Display UI has a structured button-group route; test taps separately from visual rendering. |
| `FlexBoxScope.image(bitmap = ...)` | Local `Bitmap` images are now a distinct source from remote URL images; inspect the selected signature. |
| Display tap/click callbacks | Treat app-side actions as input events with idempotent/recoverable reducers. |
| Analytics opt-out manifest metadata | `com.meta.wearable.mwdat.ANALYTICS_OPT_OUT=true` disables DAT analytics; the default is enabled. Audit disclosure, retention, and deletion separately. |
| Crash-reporting opt-out manifest metadata | `com.meta.wearable.mwdat.CRASH_REPORTING_OPT_OUT=true` disables DAT SDK crash capture; audit disclosure and retention. |
| Java-visible `DatResult` reference type | Java callers can use public DAT methods by source names; Kotlin source compatibility is not proof of Java compatibility. |
| Display builder returns changed | `ContentScope.flexBox`/`video` are builder blocks; the old returned `DisplayComponent`, `VideoScope`, and related patterns are historical. |
| `addStream`/`removeStream`, DAM opt-out, and several older error cases removed | Search migrations before copying 0.7/0.8 examples. DAM is always enabled in 0.9.0. |
| Camera Access sample supports optional sound-in-video while backgrounded | This is a sample/route signal, not a blanket background guarantee for every app or device. Verify the target and policy. |
| MockDevice phone-camera stream/R8 consumer-rule fixes | Keep Android mock and release build checks separate; a fixed mock does not prove glasses transport. |

## Swift/Kotlin boundary matrix

| Concern | iOS DAT | Android DAT | Evidence rule |
| --- | --- | --- | --- |
| Initialization | `Wearables.configure()` | `Wearables.initialize(context)` | Typecheck the selected target. |
| Session | `DeviceSession` | `DeviceSession` in the official 0.9.0 sample; `Session` remains in older upstream guidance | Same product concept; resolve the selected artifact and preserve the naming conflict until target compilation. |
| Observation | `AsyncSequence`/publisher listeners | `Flow`/`StateFlow` | Test cancellation and terminal completion on each platform. |
| Failure | Swift `throws`/typed errors | `DatResult<T,E>` and typed errors | Do not translate one error enum into the other without a mapping. |
| Camera | `addCamera(config:)` → `Camera.stream` | `addCamera(configuration)` → `Camera.stream` | Camera ownership is conceptually shared; exact signatures remain platform-specific. |
| Display | Swift display component route | Kotlin builder/Compose-style route | Rendering/input proof is target-specific. |
| Configuration | `Info.plist`, URL schemes, accessory/background/privacy keys | Manifest metadata, permissions, intent filter, Gradle credentials | Audit the actual target files. |
| Mock | `MWDATMockDevice` | `mwdat-mockdevice` | Mock evidence never proves physical behavior. |

## Privacy and release boundary

Android analytics and crash opt-outs are manifest metadata, not a substitute for
product disclosure, data retention, or deletion behavior. `APPLICATION_ID` and
`CLIENT_TOKEN` are Developer Center configuration values; Developer Mode
placeholders are not release credentials. The public repository describes
developer preview, organizations, release channels, supported device and
firmware dependencies, and tester access. Keep signed build, release channel,
App Store/Play eligibility, and production behavior as separate evidence rows.

The Android source does not establish a public “Gen 3” runtime mapping. Record
the actual model, runtime device type, firmware, Meta AI version, and capability
response; never alias a consumer label to an enum or to iOS behavior.

## Sources

- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android README](https://github.com/facebook/meta-wearables-dat-android#readme)
- [DAT Android DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess)
- [DAT Android DisplayViewModel source](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/DisplayAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/displayaccess/display/DisplayViewModel.kt)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android Codex plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
