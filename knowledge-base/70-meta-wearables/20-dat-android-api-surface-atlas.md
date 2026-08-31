# DAT Android API surface atlas

This is the Android counterpart to the [iOS API atlas](10-dat-ios-api-surface-atlas.md).
It records the public artifact, API, lifecycle, Display, MockDevice, and
debugging surface without pretending that Kotlin, Java, Swift, and Web App
names are interchangeable. It was refreshed on 2026-08-22 against Android DAT
`main` commit `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc`, the 0.9.0 changelog
dated 2026-08-03, the current upstream Android guidance, and the public DAT
reference. The package/API reference for a named target remains authoritative.

## Authority and current source conflict

Use this order when sources disagree:

1. the exact resolved Maven artifact and generated/API reference used by the
   target;
2. the same release's changelog and official sample;
3. the current Developer Center and raw `llms.txt` reference;
4. moving `main` guidance, plugin skills, and historical examples.

The current `AGENTS.md` and upstream skills still show a mixture of 0.8-era
coordinates and `Session` examples, while the 0.9.0 changelog documents the
consolidated `DeviceSession.addCamera(...)` route. Preserve this as a
`source-conflict`/compile gate. Do not decide the symbol from prose or from
Swift parity.

## Public artifact inventory

| Artifact | Public role | Evidence status |
| --- | --- | --- |
| `com.meta.wearable:mwdat-core:0.9.0` | initialization, registration, permissions, devices, selectors, session/state/error surfaces | `source`; target dependency graph still required |
| `com.meta.wearable:mwdat-camera:0.9.0` | `Camera`, `StreamConfiguration`, stream state/errors, frames, and photo capture | `source`; exact target signature still required |
| `com.meta.wearable:mwdat-display:0.9.0` | Display builder tree, text/image/icon/button/video, button groups, taps/clicks, state/errors | `source`; physical display/input still required |
| `com.meta.wearable:mwdat-mockdevice:0.9.0` | simulated glasses, permissions, lifecycle, media, and gestures | `source`/`mock` only; no hardware transport proof |

The public Android repository and upstream guidance expose four public artifact
lanes. Broader conceptual names in the full reference are discovery/index
signals, not additional Maven coordinates until an exact target resolves them.

For machine-readable routing, load the Android rows in the [source-pinned API
surface register](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
(`AND-*`). Each row carries artifact/symbol status, source anchors,
compile/runtime gate, privacy path, fallback, and migration notes; it does not
replace the resolved Maven artifact or generated API.

## Integration route

```text
Wearables.initialize(context)
  -> startRegistration(activity)
  -> registrationState / permission state / devices
  -> AutoDeviceSelector or SpecificDeviceSelector
  -> createSession(...)
  -> DeviceSession.start()
  -> addCamera(StreamConfiguration) -> Camera.stream -> start/stop/removeCamera
       or
     addDisplay(DisplayConfiguration) -> sendContent / input / stop/removeDisplay
  -> observe typed results, state/error Flow, and device compatibility
  -> stop capabilities -> stop session -> release domain resources
```

This route is a product concept, not a license to copy every name verbatim.
The selected artifact/API reference must establish whether the target exposes
`Session` or `DeviceSession`, extension functions or member methods, and the
exact `DatResult` type parameters.

## Core and configuration surface

| Concern | Current public Android route | Gate |
| --- | --- | --- |
| Repository | GitHub Packages at `maven.pkg.github.com/facebook/meta-wearables-dat-android` | use a read-only `read:packages` token outside source control |
| Initialization | `Wearables.initialize(context)` | call once before registration/session APIs |
| App identity | `com.meta.wearable.mwdat.APPLICATION_ID` and `CLIENT_TOKEN` manifest metadata | developer placeholders are not release credentials |
| Callback | intent filter with the target URL scheme | route the callback to the selected SDK handler |
| Permissions | Bluetooth/Internet manifest and runtime permissions plus DAT/Meta AI permission state | observe denial and recovery, not only OS grant |
| Registration | `Wearables.startRegistration(activity)`, `registrationState`, registration errors | wait for the registered state before creating a session |
| Device selection | `Wearables.devices`, metadata, `AutoDeviceSelector`, `SpecificDeviceSelector` | use link/compatibility/display predicates from the target artifact |
| Update navigation | firmware and on-glasses DAT-app update actions in the public route | record attempted and observed post-update state separately |

Keep `APPLICATION_ID`, `CLIENT_TOKEN`, GitHub tokens, release-channel values,
and diagnostic payloads out of source, logs, fixtures, and portable archives.

## Session and result surface

| Surface | Public 0.9 signal | Implementation consequence |
| --- | --- | --- |
| Session naming | The official 0.9.0 DisplayAccess sample imports `DeviceSession`; moving upstream `AGENTS.md`/plugin guidance still uses `Session` | resolve against the generated API of the exact artifact; retain the source conflict and add a compile fixture |
| Lifecycle | `IDLE`, `STARTING`, `STARTED`, `PAUSED`, `STOPPING`, `STOPPED` in upstream route/changelog lineage | treat terminal stop as a release of the session and recreate rather than reuse |
| Result | `DatResult` carries typed success/failure; 0.9 makes it Java-visible | surface failures at every initialization/session/capability boundary |
| Observation | Kotlin `Flow`/`StateFlow` for registration, devices, session, stream, and errors | cancel collectors with screen/session ownership and test terminal completion |
| Camera ownership | 0.9 consolidates camera under `Camera` with child `Camera.stream` | stop child stream/camera before parent session and reject stale frames |
| Display ownership | Display attaches to a started session and has its own state/errors | gate content on runtime Display capability and clear/stop explicitly |

## 0.9 migration atlas

| Release signal | Search for | 0.9 action |
| --- | --- | --- |
| Camera consolidation | `addStream`, `removeStream`, direct stream attachment | use `addCamera` → `Camera.stream`; verify `removeCamera` and exact configuration signature |
| Display builder changes | `DisplayComponent`, `VideoScope`, returned `flexBox`/`video` values | compose through the current builder blocks and typecheck the target |
| Button groups and taps | missing `buttonGroup`, no click callback, visual-only tests | add button-group layout and tap/click reducer tests; run a physical input task when available |
| Local image source | URL-only `image` assumptions | distinguish local `Bitmap` from remote URL and audit storage/network policy |
| Java surface | Kotlin inline `DatResult` assumptions | verify Java-visible signatures and run a Java interop compile if Java is in scope |
| DAM | `com.meta.wearable.mwdat.DAM_ENABLED=true` copied from 0.7 | 0.9 says DAM is always enabled; preserve the key only as a migration check until target compile proves behavior |
| Removed errors | `THERMAL_EMERGENCY`, `CAPABILITY_DENIED`, old session errors | map the selected 0.9 error set explicitly; do not catch everything as unknown |
| Mock/R8 | mock stream stopping or missing internal classes under minify | include the 0.9 mock and minified-build fixtures as separate evidence rows |

## Camera, audio, and data boundary

The public Android camera route covers video frames and photo capture through
the camera artifact. The Android CameraAccess sample also contains a phone-side
`AudioRecord` path for sound-in-video. That sample is not evidence of a glasses
HFP microphone API or of an always-on background audio contract.

The reusable [Android camera starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt)
keeps `VideoFrame` values inside the adapter, exposes only bounded first-frame
and photo events, and remains a Maven-backed compile gate.

For camera/audio work, record:

- camera/Meta AI permission and the exact capture route;
- frame ownership, bounded processing, cancellation, and photo retention;
- whether audio is phone microphone, glasses HFP, or playback output;
- consent, disclosure, network/storage, vendor processing, thermal, and
  background behavior;
- source, compile, mock, connected, and physical evidence independently.

## Native Display surface

The Android Display lane is a separate native capability, not Web App DOM:

- builder content includes `FlexBox`, text, icons, images, buttons, video, and
  0.9 button groups;
- local `Bitmap` images and remote URL images are distinct data paths;
- 0.9 adds Display tap/click callbacks that must become typed, idempotent input
  events in the app reducer;
- Display has lifecycle/error state and video constraints; each content send
  replaces the current root surface;
- runtime `isDisplayCapable`/compatibility filtering is a prerequisite, not a
  cosmetic UI choice.

Browser or MockDevice rendering can establish layout and reducer behavior. It
cannot establish optical legibility, Neural Band/captouch behavior, link
quality, firmware compatibility, or physical Display reliability.

## MockDevice and debugging

The public mock route can cover registration, permission outcomes, paired model
fixtures, power/fold/don/doff transitions, camera feeds, photo behavior, and
captouch simulation. Label all results `mock` and retain the physical follow-up
for Bluetooth, optics, HFP, thermal, firmware, and input.

Use public MCP/static reference search for source discovery. If a local DAT
debug server is available, export only redacted app-visible readiness, device
path, state, permission, error, and event-digest evidence. It is not companion
app introspection and does not authorize a release claim.

## Android surface evidence rows

| ID | Surface | Minimum evidence | Not proven by that evidence |
| --- | --- | --- | --- |
| `AND-SOURCE-01` | four artifact coordinates and selected API reference | pinned source snapshot | target compilation |
| `AND-CONFIG-01` | Gradle, manifest, callback, permissions, app identity | static config review | registration or physical link |
| `AND-API-01` | session/camera/Display symbols | generated API or compile fixture | hardware behavior |
| `AND-MIGRATE-01` | 0.9 camera/Display/DAM/result changes | migration test or compile result | release-channel compatibility |
| `AND-MOCK-01` | registration, lifecycle, media, input | MockDevice test | radio, optics, HFP, firmware, thermal |
| `AND-BUILD-01` | debug/release/R8/Java interop | reproducible build/test output | signed release-channel access |
| `AND-PHYS-01` | named glasses/firmware/companion/operation | connected physical run | another model or “Gen 3” alias |
| `AND-RELEASE-01` | app identity, tester/channel, signed artifact | release evidence packet | public production approval |

## Unresolved labels and source conflicts

- The public Android source names Gen 2, Optics, Meta Glasses, and Display
  families through the selected model surface and announcements, but it does
  not establish the user's “Gen 3” wording as a runtime enum. Keep it
  `to-verify`.
- The current upstream examples contain 0.8 coordinates and `Session` names;
  the 0.9 changelog is newer but still requires target artifact compilation.
- The full reference and Web Apps toolkit remain separate from native Android
  DAT. Web App features must not be imported as Android APIs.

## Sources

- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android `AGENTS.md`](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [Android DAT API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
