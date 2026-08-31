# Android DAT 0.9.0 migration fixture

Use this compact fixture with the Android integration role. It is synthesized
from the public Android repository and changelog at the 0.9.0 source snapshot;
typecheck every exact symbol against the resolved Maven artifacts.

| Area | Current 0.9 route | Historical trap |
| --- | --- | --- |
| Dependency | `com.meta.wearable:mwdat-core/camera/display/mockdevice:0.9.0` | An iOS product name or an unreleased Maven version. |
| Initialization | `Wearables.initialize(context)` | Calling APIs before initialization. |
| Session | `Wearables.createSession(selector)` → `DeviceSession.start()` in the official 0.9.0 DisplayAccess sample | Some older upstream guidance still says `Session`; resolve the selected artifact before compiling. Reusing a terminal session or assuming a session streams automatically is still invalid. |
| Camera | `session.addCamera(config)` → `camera.stream` → `camera.stop()`/`removeCamera()` | `addStream()`/`removeStream()` direct capability route. |
| Result handling | `DatResult<T,E>` with typed failure | `getOrThrow()` in user-facing paths or assuming Swift `throws` parity. |
| Display | Builder blocks, button groups, local/remote images, tap callbacks | Returning `DisplayComponent`, `VideoScope`, or old DAM setup. |
| Mock | `mwdat-mockdevice`, lifecycle/media/permission fixtures, R8 consumer rules | Mock pass treated as transport/optics/input proof. |
| Privacy | Manifest `ANALYTICS_OPT_OUT`/`CRASH_REPORTING_OPT_OUT` controls, app/client metadata, Android permissions | Credentials or raw media placed in source/logs; opt-out metadata is not a complete product privacy policy. |

## Sources

- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
