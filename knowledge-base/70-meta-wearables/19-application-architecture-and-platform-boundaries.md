# Application architecture and platform boundaries

The full Meta Wearables surface is not one interchangeable SDK. A maintainable
product has a shared domain and policy layer, platform-specific DAT adapters,
native Display or Web App presenters, and a phone-first fallback. This page is
the implementation bridge between the source matrix and a real iOS/Android
target.

Reviewed 2026-08-22 against the DAT iOS/Android 0.9.0 source snapshot, the public
Web Apps toolkit, and the full DAT reference. Exact symbols remain package and
target compile gates.

## Recommended boundary map

| Layer | Owns | Keep out |
| --- | --- | --- |
| Product/domain | User intent, typed state, capability request, privacy policy, fallback, retention | DAT imports, Web APIs, account secrets |
| Wearable coordinator | Registration/session epochs, device/capability selection, event reduction, resource ownership | SwiftUI/Compose view mutation, raw-media persistence |
| iOS adapter | SPM products, callback, permissions, `DeviceSession`, camera/audio/Display translation | Shared domain decisions and view layout |
| Android adapter | Maven artifacts, Manifest/configuration, `Flow`/`StateFlow`, `DatResult`, capability translation | Swift symbols and iOS configuration assumptions |
| Native Display presenter | Compact sanitized Display tree, focus/action mapping, clear/stop | Web DOM and phone navigation source of truth |
| Web App surface | Public HTTPS HTML/CSS/JS, 600×600/additive display, focus/input, hosted data | Native DAT imports and private tokens |
| Phone fallback | Setup, detailed content, manual input, cached/typed unavailable state | A claim that it is glasses-native |

“Full SDK” means the requested capability has been audited across the relevant
modules, lifecycle, privacy, fallback, and evidence gates. It does not mean that
every app should import every module or that the iOS, Android, and Web App APIs
can be flattened into one symbol set.

## Canonical lifecycle

Keep these gates distinct:

```text
unconfigured
  -> companionUnavailable | registrationRequired
  -> registering
  -> permissionRequired | deviceSelectionRequired | ready
  -> sessionStarting
  -> connected
  -> capabilityStarting
  -> active
  -> paused | disconnected | unsupported | thermalLimited | failed
  -> stopping
  -> ready | unavailable | failed
```

Registration, permission, device selection, session, and capability are separate
states. A callback, paired device, or successful session does not prove camera,
HFP audio, Display, Web App input, or remote-service availability.

Every asynchronous operation needs a session epoch or equivalent generation.
Events from an old epoch must not mutate current state, send stale Display
content, append frames to a new consumer, or resurrect a stopped session.
Terminal stop owns cancellation, stream/collector closure, capability release,
Display cleanup, and the transition back to a restartable state.

## Platform adapter contract

Define product-level seams such as:

```text
WearableCoordinator
  register() / unregister()
  observeState() -> AppWearableState
  selectDevice(criteria)
  startSession() / stopSession()

CameraCapability
  start(configuration) -> FrameMetadata stream
  capturePhoto() -> TypedPhotoResult
  stop()

DisplayCapability
  present(sanitizedSnapshot)
  handleAction(action)
  clear()

FallbackSurface
  presentUnavailable(reason)
  continueOnPhone(intent)
```

The actual iOS adapter owns the selected MWDAT package and translates its
`AsyncSequence`/publisher and lifecycle semantics. The Android adapter owns the
selected Maven artifacts and translates its `Flow`/`StateFlow`/`DatResult`
semantics. Web Apps remain a hosted surface with their own runtime contract.
The shared layer should expose typed product state and error categories, not
platform SDK objects.

## Capability-specific boundaries

| Capability | Architecture rule | Required fallback |
| --- | --- | --- |
| Registration | Keep URL/callback and account/channel state in the integration adapter | Phone setup and explicit registration-required state |
| Camera | One owner controls the selected release’s `Camera` resource, bounded frame consumer, photo result, and stop | Phone camera/manual input or unavailable state |
| HFP/A2DP | Name phone mic, HFP glasses mic, and A2DP output separately; keep AVAudioSession or Android route code in adapter | Phone mic/manual text only with consent |
| Native Display | Gate on runtime capability; project a compact sanitized snapshot; model input/focus/clear/stop | Phone detail/action surface |
| Web App | Keep HTTPS, 600×600, additive content, focus/input, and deployment outside native DAT | Phone/manual/online/error/exit fallback |
| Sensors/remote AI | Classify processing and network/storage path before exposing data | Typed unknown/denied/offline state |

Do not use a common interface to hide a real platform difference. Return
`unsupported`, `to-verify`, `permissionDenied`, `disconnected`, or
`remoteRequired` explicitly when the target cannot provide the requested seam.

## Data and concurrency contract

For each feature, record the path:

```text
source -> adapter -> bounded processing -> optional network/vendor
       -> optional storage/logs -> user-visible projection -> deletion
```

Classify each stage as `glasses-native`, `phone-local`, `remote`, `mixed`, or
`unknown`. Keep raw frames/audio outside shared state unless explicitly needed;
prefer metadata, typed handles, bounded buffers, and user-controlled retention.

One coordinator owns registration and session lifecycle. One capability owner
owns camera/audio/Display. Views send intents and render projections. The
architecture must define cancellation and cleanup for app backgrounding,
permission revocation, scene recreation, disconnect, doff/fold, thermal/power,
and terminal stop.

## Test seams and evidence

1. Test the shared reducer/domain with deterministic event sequences, duplicate
   intents, stale epochs, cancellation, fallback, and terminal stop.
2. Test platform fakes for translation, error categories, lifecycle, and
   resource ownership.
3. Use DAT MockDevice and the Web App browser simulator for deterministic logic
   and layout only.
4. Build the selected package/artifact and inspect actual products/symbols,
   permissions, privacy metadata, and target configuration.
5. Run the same script on the named connected/physical pair, recording model,
   firmware, companion, build, capability response, and operation.
6. Repeat signed release-channel checks separately. No shared reducer, mock,
   browser, compile, or Developer Mode result is physical or production proof.

## Architecture evidence tasks

| ID | Task | Minimum evidence |
| --- | --- | --- |
| `ARCH-SOURCE-01` | Freeze the selected DAT/Web App sources, package/artifact revision, and platform boundary. | `source` |
| `ARCH-STATIC-01` | Inspect target/module boundaries, adapter imports, configuration, privacy metadata, state owner, fallback, and resource owner. | `static` |
| `ARCH-TEST-01` | Exercise shared reducer, platform fake, cancellation, stale epoch, duplicate intent, and terminal cleanup fixtures. | `build`/`fixture` |
| `ARCH-MOCK-01` | Run DAT MockDevice/browser simulator through registration, denial, disconnect, unsupported, media/Display stop, and fallback. | `mock`/`browser-sim` |
| `ARCH-PHYS-01` | Run the selected capability script on the named target pair with exact model/firmware/companion/build metadata. | `connected`/`physical` |
| `ARCH-RELEASE-01` | Repeat architecture-critical flows through the signed release channel and record fallback/recovery. | `signed`/`release-channel` |

## Sources

- [DAT iOS foundations](01-dat-ios-sdk-foundations.md)
- [DAT Android parity and boundaries](14-dat-android-parity-and-boundaries.md)
- [Full DAT SDK capability and source-conflict matrix](15-full-sdk-capability-and-source-conflict-matrix.md)
- [On-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
- [Operational readiness and recovery](18-operational-readiness-and-recovery.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [DAT-filtered full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
