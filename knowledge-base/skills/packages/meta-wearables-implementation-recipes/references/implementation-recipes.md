# Meta Wearables implementation recipes

This reference provides source-aligned implementation shapes for the selected
API rows and playbooks. It is deliberately not a copy-paste SDK sample: exact
generated signatures, package products, permissions, and target behavior must
be resolved against the pinned release before code is expected to compile.

## Contents

- [Recipe contract](#recipe-contract)
- [Shared domain and adapter shape](#shared-domain-and-adapter-shape)
- [iOS DAT session and camera](#ios-dat-session-and-camera)
- [MockDevice fixtures](#mockdevice-fixtures)
- [iOS native Display](#ios-native-display)
- [Android DAT session and camera](#android-dat-session-and-camera)
- [Android native Display](#android-native-display)
- [Android DAT target starter](#android-dat-target-starter)
- [Ray-Ban Display Web App](#ray-ban-display-web-app)
- [On-device and privacy gates](#on-device-and-privacy-gates)
- [Verification ladder](#verification-ladder)
- [Implementation handoff](#implementation-handoff)
- [Sources](#sources)

## Recipe contract

Freeze this packet before generating code:

| Field | Example shape | Rule |
| --- | --- | --- |
| `outcome` | “Show the next appointment and let the wearer dismiss it.” | One user result, not a feature inventory. |
| `primary_surface` | `ios-dat-display` | Name native DAT, native Display, Web App, or phone. |
| `fallback_surface` | `ios-phone-detail` | Preserve the outcome when the wearable route fails. |
| `target_tuple` | app target, OS, package/artifact, runtime, phone, firmware, channel | Unknown values remain `to-verify`. |
| `api_rows` | `IOS-SESSION-001`, `IOS-DISPLAY-001`, `GEN-PHYSICAL-01` | Copy IDs from the manifest/evidence packet. |
| `data_path` | `phone-local` | Classify every media/audio/sensor/network hop. |
| `owner` | `WearableCoordinator` + `DisplayCapability` | One lifecycle owner per resource. |
| `proof` | `build` then `physical` | Do not skip evidence levels. |

## Shared domain and adapter shape

Share outcome policy and typed events, not SDK symbols:

```text
DomainEvent
  registrationChanged(status)
  deviceChanged(snapshot)
  capabilityChanged(kind, status)
  displayActionReceived(action)
  operationCompleted(result)
  operationFailed(category)
  fallbackRequested(reason)

WearableCoordinator
  owns registration + session epoch
  starts/stops exactly one selected capability
  rejects events from old epochs
  projects sanitized domain state to the surface
  returns typed phone fallback

IOSAdapter       -> AsyncSequence/publisher translation
AndroidAdapter   -> Flow/StateFlow/DatResult translation
WebAppAdapter    -> DOM/host/input/exit translation
PhoneAdapter     -> always-available local outcome where possible
```

Every adapter must expose the same product intent without exposing
`MWDAT*`, Kotlin classes, browser `Event`, `CMSampleBuffer`, `AudioRecord`,
raw audio, or raw frame queues to the shared reducer.

## iOS DAT session and camera

Use `IOS-CORE-001`, `IOS-REG-001`, `IOS-PERM-001`, `IOS-DEVICE-001`,
`IOS-SESSION-001`, `IOS-CAMERA-001`, and `IOS-MEDIA-001`. The 0.9 source
contract consolidates camera ownership under `DeviceSession.addCamera(config:)`;
the returned `Camera` owns `Camera.stream` and is stopped before the session.

The [source-aligned iOS camera starter](../assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift)
is a compile-tested DAT 0.9.0 seed against the selected target's simulator
`MWDATCore`/`MWDATCamera` frameworks. It keeps raw frames inside the adapter,
exposes first-frame/photo events, and sends photo bytes only through an explicit
phone-local sink. Compile the asset against the selected package before adding
decoding, recording, inference, storage, or network work.

Illustrative shape; resolve every marked signature against the selected SPM
product and generated API:

```swift
actor WearableCameraAdapter {
    private var epoch = 0
    private var session: DeviceSession?
    private var camera: Camera?

    func start(_ configuration: CameraConfiguration) async throws {
        epoch += 1
        let current = epoch

        // COMPILE GATE: resolve selector/configuration types in the pinned SDK.
        let nextSession = try Wearables.createSession(deviceSelector: selector)
        try await nextSession.start()
        let nextCamera = try nextSession.addCamera(config: configuration)

        session = nextSession
        camera = nextCamera

        // BOUNDARY: consume a bounded stream and reject frames whose epoch is
        // no longer current. Keep conversion/model work phone-local if chosen.
        for await frame in nextCamera.stream {
            guard current == epoch else { break }
            await boundedConsumer.accept(frame)
        }
    }

    func stop() async {
        epoch += 1
        await camera?.stop()
        await session?.stop()
        camera = nil
        session = nil
    }
}
```

Do not infer that the snippet compiles from the changelog. Confirm whether the
selected target uses `async throws`, a publisher, or another generated overload;
the 0.9 migration and `CameraState`/stream terminal behavior are the authority.
Background, doff/hinge, thermal, denial, disconnect, queue overflow, and photo
failure must all stop the camera and return to the phone route.

## MockDevice fixtures

Use `IOS-MOCK-001`, `AND-MOCK-001`, `ODC-MOCK-01`, and `ARCH-MOCK-01` for
deterministic fixture work. The [iOS MockDevice starter](../assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift)
is type-checked against the selected DAT 0.9.0 `MWDATCore` and
`MWDATMockDevice` simulator frameworks. It centralizes enable/configure,
`.rayBanMeta` pairing, power/fold/don/doff lifecycle, camera permission status
and request results, file or phone-camera feeds, captured images, and captouch
triggers.

The [Android MockDevice starter](../assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt)
follows the official DAT 0.9.0 `MockDeviceKit`/`MockGlasses` sample with
`DatResult.fold` pairing, lifecycle controls, `Permission` outcomes, URI or
phone-camera feeds, captured images, and `captouch` actions. It remains
compile-open until the selected Android Maven target resolves. On both
platforms, configure the mock in test setup, run adapter/reducer assertions,
stop app-owned capability/session children, and unpair/disable in teardown.

When UI tests need to control a mock server from a separate process, use the
[iOS MockDevice test-client starter](../assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift).
The app process owns `MockDeviceKitInterface.startTestServer(portFilePath:)`;
the UI-test process owns `MockDeviceTestClient(portFilePath:)`, waits for the
server, pairs by the explicit `.rayBanMeta` device type, drives sanitized
lifecycle/media/captouch actions, and unpairs during teardown. This is the
test-only fifth iOS product in the source manifest, not a runtime capability.

Keep media inputs out of the package and logs. Use HEVC/H.265 video and
JPEG/PNG images when file-backed camera behavior is required. Runtime Android
permission grants belong to the instrumentation target rather than this
reusable harness. Mock output establishes deterministic state and failure
handling only; it does not prove radio, optics, audio routing, firmware,
thermal behavior, physical input, or a Gen 2/Gen 3 device claim.

## iOS native Display

Use `IOS-DEVICE-001`, `IOS-SESSION-001`, `IOS-DISPLAY-001`, `IOS-DEVICE-OPS-001`,
and `GEN-PHYSICAL-01`. Gate on the runtime `supportsDisplay()` predicate, not
on “Gen 2”, “Gen 3”, or a consumer product name.

The [native iOS Display starter](../assets/meta-wearables-ios-display-starter/MetaWearablesDisplayStarter.swift)
is a compile-tested DAT 0.9.0 seed against the pinned iOS XCFrameworks. It
keeps the product boundary typed, uses `DeviceSession` state/error streams,
attaches a `Display` with `session.addDisplay()`, sends a complete `FlexBox`,
and cancels the listener before stopping the Display and its parent session.
Adapt the event sink and snapshot only after checking the selected target's
SPM product and privacy configuration.

```swift
struct DisplaySnapshot: Sendable {
    let title: String
    let detail: String
}

@MainActor
final class DisplayCapability {
    private var epoch = 0
    private var session: DeviceSession?
    private var display: Display?
    private var displayStateToken: (any AnyListenerToken)?

    func attach(to session: DeviceSession) throws {
        let nextDisplay = try session.addDisplay()
        self.session = session
        display = nextDisplay
        displayStateToken = nextDisplay.statePublisher.listen { state in
            // Translate DisplayState to a product event on the main actor.
            _ = state
        }
        nextDisplay.start()
    }

    func present(_ snapshot: DisplaySnapshot) async throws {
        guard let display, display.state == .started else { return }
        let current = epoch
        let card = FlexBox(direction: .column, spacing: 12) {
            Text(snapshot.title, style: .heading)
            Text(snapshot.detail, style: .meta, color: .secondary)
            ButtonGroup(alignment: .center) {
                Button(
                    label: "Do it",
                    style: .primary,
                    iconName: .checkmark,
                    onClick: {
                        guard current == epoch else { return }
                        // Emit a typed product action here.
                    }
                )
            }
        }
        try await display.send(card.padding(24).background(.card))
    }

    func stop() async {
        epoch += 1
        let token = displayStateToken
        displayStateToken = nil
        await token?.cancel()
        display?.stop()
        display = nil
        session?.stop()
        session = nil
    }
}
```

Keep text short and payloads sanitized. Test focus, button-group/input,
replacement, clear, timeout, disconnect, legibility, and phone handoff. The
physical Display task is the only proof of optics, brightness, input timing,
or firmware behavior.

## Android DAT session and camera

Use `AND-CORE-001`, `AND-DEVICE-001`, `AND-SESSION-001`, `AND-CAMERA-001`,
`AND-AUDIO-001` when audio is present, and `AND-PHYS-01`. The 0.9 source
contract uses `DeviceSession.addCamera(streamConfiguration)`, `Camera.stream`,
`Camera.stop()`, and `removeCamera()`; direct `addStream()` is removed.

The [source-aligned Android camera starter](../assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt)
follows the official 0.9.0 `CameraAccess` shape: `DatResult` permission and
camera operations, `Flow` session/stream collectors, `Camera.stream`, photo
capture, raw-frame containment, and camera-before-session teardown. It remains
compile-open because this repository has no authenticated Android Maven target.

```kotlin
class WearableCameraAdapter(
    private val scope: CoroutineScope,
    private val events: (DomainEvent) -> Unit
) {
    private var epoch = 0L
    private var session: DeviceSession? = null
    private var camera: Camera? = null

    suspend fun start(configuration: StreamConfiguration) {
        val current = ++epoch
        // COMPILE GATE: resolve initialization/session result unwrapping and
        // selector/configuration types in the pinned Maven artifacts.
        val nextSession = Wearables.createSession(deviceSelector)
        nextSession.start()
        val nextCamera = nextSession.addCamera(configuration)
        session = nextSession
        camera = nextCamera

        scope.launch {
            nextCamera.stream.collect { frame ->
                if (current == epoch) boundedConsumer.accept(frame)
            }
        }
    }

    suspend fun stop() {
        ++epoch
        camera?.stop()
        // COMPILE GATE: use the artifact's DatResult/close/remove contract.
        session?.stop()
        camera = null
        session = null
    }
}
```

The exact artifact may expose `DatResult` wrappers or suspend/`Flow` variants;
unwrap them at the Android adapter boundary. Record the selected min/compile
SDK, manifest permissions, R8 rules, and Java-visible API if Java callers are
in scope. Keep the phone microphone `AudioRecord` sample distinct from a
glasses microphone claim.

## Android native Display

Use `AND-SESSION-001`, `AND-DISPLAY-001`, `AND-DEVICE-001`, and `AND-PHYS-01`.
The [native Android Display starter](../assets/meta-wearables-android-display-starter/MetaWearablesAndroidDisplayStarter.kt)
is source-aligned to the official Android 0.9.0 DisplayAccess sample. It keeps
registration, permission, device-picker, and Android UI policy in the target
app, while the reusable coordinator owns the selected session, `Flow`
collectors, typed fallback, stale-content epochs, and child-before-parent
teardown. It remains an explicit Android compile gate because this repository
does not resolve the private Maven artifacts.

Gate on the selected runtime Display capability and compose a complete,
sanitized root through the 0.9 builder API:

```kotlin
fun present(snapshot: DisplaySnapshot, display: Display) {
    // COMPILE GATE: resolve the selected artifact and builder receiver types.
    display.sendContent {
        flexBox(direction = Direction.COLUMN, gap = 12, padding = 24) {
            text(snapshot.title, style = TextStyle.HEADING)
            text(snapshot.detail, style = TextStyle.META, color = TextColor.SECONDARY)
            buttonGroup {
                button(
                    "Do it",
                    style = ButtonStyle.PRIMARY,
                    iconName = IconName.CHECKMARK,
                    onClick = { events.emit(DomainEvent.DisplayAction) },
                )
            }
        }
    }
}

fun stop(session: DeviceSession) {
    // The current official Android 0.9 sample detaches through the parent.
    session.removeDisplay()
    session.stop()
}
```

The 0.9 Android surface includes button groups, local `Bitmap` images, and tap/
click routing, but each must be resolved and tested against the actual artifact.
Do not port iOS `FlexBox`/`Button` names mechanically, and do not infer that a
Maven coordinate or source-aligned snippet proves a named pair can render or
accept input.

## Android DAT target starter

When the selected Android route has no Gradle target, begin with the
[credential-safe Android target starter](../assets/meta-wearables-android-target-starter/README.md).
It is deliberately smaller than the official DisplayAccess sample: the target
owns Android permission requests, `Wearables.initialize(context)`, manifest
metadata, the GitHub Packages repository, and a visible phone bootstrap state;
the selected capability adapter remains a separate next slice.

The starter freezes the source-observed Android 0.9.0 full-artifact build graph—AGP `8.11.1`,
Kotlin `2.2.21`, Gradle `8.14.1`, compile/target SDK `36`, min SDK `31`, Java/Kotlin
JVM `17`, and `mwdat-core`, `mwdat-camera`, `mwdat-display`, and
`mwdat-mockdevice` `0.9.0`. It accepts `GITHUB_TOKEN`,
`MWDAT_APPLICATION_ID`, and `MWDAT_CLIENT_TOKEN` through the environment, with
ignored `local.properties` as the local fallback. It contains no real values.

The starter is not compiled in this repository because the Android SDK, Gradle
executable, and authenticated Maven path are absent. After copying it into a
sibling target, run `gradle :app:assembleDebug`, record the target-preflight
receipt, and only then add the native Display/camera/audio route. A successful
target build still does not establish registration, named-device capability,
physical optics/input, Gen 2/Gen 3 behavior, signing, or release evidence.

## Ray-Ban Display Web App

Use `WEB-RUNTIME-001`, `WEB-INPUT-001`, `WEB-SIM-001`, `WEB-NET-001`,
`WEB-PHYSICAL-001`, and `WEB-CONFLICT-001` only for separately tested features.
Keep the hosted surface additive, compact, high-contrast, focusable, and within
the documented 600×600 target. The page must have a phone fallback and a clear
host-exit/network/error state.

```html
<main id="app" tabindex="-1" aria-live="polite">
  <h1 id="title"></h1>
  <button id="primary" type="button"></button>
</main>
<script type="module">
  const state = { epoch: 0, focused: 0, online: navigator.onLine };
  const controls = [document.querySelector('#primary')];

  function render(snapshot) {
    document.querySelector('#title').textContent = snapshot.title;
    controls[0].textContent = snapshot.primaryAction;
    controls[0].focus();
  }

  document.addEventListener('keydown', (event) => {
    // Host/input semantics are a runtime gate; test D-pad/EMG mapping in the
    // browser simulator and on a named physical Display pair.
    if (event.key === 'Enter') controls[state.focused]?.click();
    if (event.key === 'Escape') phoneFallback('host-exit');
  });
  window.addEventListener('offline', () => phoneFallback('network-unavailable'));
  window.addEventListener('pagehide', () => { state.epoch += 1; });
</script>
```

Use the toolkit’s current skill guidance as a source to test text input,
offline/cache, back/escape, extended gestures, motion/orientation, and
geolocation independently because the public full reference and toolkit have
source conflicts. Never put private tokens in browser code or query strings.

The portable [Web App starter](../assets/meta-wearables-web-starter/) is a
dependency-free 600×600 HTML shell plus a pure reducer for focus, stale input,
network/timeout/error handling, host exit, and phone fallback. Run its tests
from the implementation-recipes package directory:

```sh
node --test assets/meta-wearables-web-starter/test/display-state.test.mjs
```

The starter deliberately does not guess host globals or import the moving
toolkit. Its passing Node tests prove reducer and bounded-projection behavior;
the selected toolkit revision, browser simulator, public HTTPS deployment,
named Display pair, firmware, and physical optics/input run remain separate
evidence gates.

## On-device and privacy gates

For every recipe, return a data-flow table:

| Data | Source | Processing | Retention | Network | Fallback |
| --- | --- | --- | --- | --- | --- |
| camera frame | glasses DAT camera | phone-local / remote / unknown | bounded memory or explicit save | none / approved endpoint | phone camera/manual |
| audio | phone mic / HFP / A2DP | phone-local / remote / unknown | no raw default | explicit consent | text/manual |
| Display text | product state | phone-generated projection | transient | none by default | phone detail |
| sensor/input event | Display/Web App/phone | local reducer | transient | none by default | touch/manual |

“On-device” is not a blanket product label. State whether computation is
glasses-native, phone-local, remote, mixed, or unknown and identify the exact
evidence needed to close the claim.

## Verification ladder

| Level | Recipe proof | Does not prove |
| --- | --- | --- |
| Source | row, changelog, reference, migration | compile or hardware |
| Static | target graph, config, privacy, ownership | runtime behavior |
| Build | selected package/artifact and symbols compile | physical optics/radio |
| Reducer/mock/browser | cancellation, stale epoch, layout, fallback | named glasses behavior |
| Connected | exact pair/companion/firmware reports operation | release-channel/production |
| Physical | optics, audio, input, camera, recovery task | universal model parity |
| Signed/release | exact channel build and hosted revision | all device variants |

## Implementation handoff

```text
recipe: ios-camera | ios-display | android-camera | android-display | webapp | shared-outcome
playbook: A | B | C | D | E
outcome: <one sentence>
target_tuple: <app/OS/package-or-artifact/runtime/phone/companion/firmware/channel>
api_rows: <IOS-*/AND-*/WEB-*/compatibility/evidence IDs>
imports_or_symbols: <confirmed / to-verify with reason>
state_owner: <coordinator and capability owner>
stop_order: <child capability -> session -> fallback>
data_path: <classification for every data type>
tests: <reducer/fake/mock/browser/build/connected/physical tasks>
open_gates: <source/compile/privacy/account/device/release gaps>
refresh_trigger: <release/API/toolkit/device/access change>
```

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [DAT Android API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Portable API manifest](../../meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Vertical-slice playbooks](../../meta-wearables-app-architecture/references/vertical-slice-playbooks.md)
