# Meta Wearables architecture contract

Use this contract to turn a feature request into an implementation plan that
survives platform differences, missing hardware, and SDK version changes.

## Boundary map

| Layer | Owns | Must not own |
| --- | --- | --- |
| Product/domain | User intent, capability request, policy, typed state, fallback, retention decision | DAT imports, Swift/Kotlin/Web API symbols, account secrets |
| Wearable coordinator | Registration/session epochs, device/capability selection, event reduction, resource ownership | View layout, raw media persistence, unsupported platform assumptions |
| iOS adapter | SPM products, MWDAT configuration, registration callback, `AsyncSequence`/publisher translation, camera/audio/Display lifecycle | Shared domain decisions or direct view mutation |
| Android adapter | Maven artifacts, Manifest/configuration, Kotlin `Flow`/`StateFlow`, `DatResult`, camera/Display lifecycle | Swift symbols, iOS config, shared assumptions about errors |
| Native Display presenter | Compact sanitized native Display tree, focus/action mapping, clear/stop | Web DOM, phone navigation source of truth |
| Web App surface | HTTPS HTML/CSS/JS, 600×600/additive UI, focus/input, hosted data boundary | Native DAT imports, private tokens, unverified browser APIs |
| Phone fallback | Useful setup, detailed content, manual input, cached/typed unavailable state | Pretending to be a glasses capability |
| Evidence/test layer | Reducer tests, fakes, MockDevice/browser, connected/physical/release scripts | Treating lower evidence as higher proof |

The shared layer can use concepts such as `RegistrationState`,
`PermissionState`, `DeviceSnapshot`, `SessionState`, `CapabilityState`,
`DisplayIntent`, and `FallbackReason`. It must not expose a platform SDK type
as the product contract.

## Canonical lifecycle

Use only the states that the product needs, but preserve the distinctions:

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

Rules:

1. Every asynchronous start receives a session epoch. Events from an old epoch
   cannot mutate the current state or send a Display action.
2. Registration, permission, session, and capability are separate gates; a
   callback or paired device does not imply the next gate is open.
3. `paused`, `disconnected`, `thermalLimited`, and `stopping` are not generic
   errors. They require the adapter’s documented recovery or fallback policy.
4. Terminal stop closes streams/collectors, cancels frame/audio work, clears or
   replaces Display content where required, and releases the capability before
   the next session begins.
5. A user intent is idempotent by operation ID. Duplicate taps, callbacks, or
   reconnect events must not create multiple sessions or capability owners.

## Capability adapter table

| Product seam | iOS adapter | Android adapter | Web App/phone behavior |
| --- | --- | --- | --- |
| Registration | MWDAT registration and URL handling from selected package | `Wearables` registration/activity callback from selected artifact | Hosted add/launch flow; phone owns setup |
| Device selection | Current device stream/selector and capability predicate | Device/selector flow and capability predicate | Runtime glasses/host launch; no native DAT import |
| Session | `DeviceSession` state/error streams from selected release | Current session API and `Flow`/`DatResult` from selected artifact | Page lifecycle and host disconnect/exit |
| Camera | `addCamera`/`Camera.stream`/stop in the selected iOS release | `addCamera`/`Camera.stream`/stop in the selected Android artifact | No camera contract unless current official runtime proves one |
| HFP/A2DP audio | AVAudioSession route and DAT-supported path, separately named | Exact artifact audio path; do not infer from iOS | Browser audio capability remains source/runtime-gated |
| Native Display | MWDATDisplay tree, capability gate, input, clear/stop | mwdat-display builder/input/clear/stop | Not interchangeable with Web DOM |
| Fallback | SwiftUI/AVFoundation/local state | Compose/View/local state | Phone/manual/online/error fallback |

The table is an architecture map, not a permission to copy symbols. Resolve
the selected package/API reference and compile the target before implementing a
seam.

## Event translation

Adapters should translate platform events into a small domain event set:

```text
companionChanged
registrationChanged
permissionChanged
deviceSnapshotChanged
sessionStateChanged
capabilityStateChanged
frameMetadataReceived
audioRouteChanged
displayActionReceived
thermalChanged
transportChanged
operationFailed
```

Keep raw frames/audio outside the shared event bus unless the feature’s data
contract explicitly requires them. Prefer bounded metadata or typed handles;
make ownership and deletion explicit. Preserve the original platform error
category and source revision alongside a user-safe error.

## Concurrency and ownership

- One coordinator owns registration/session lifecycle per target process.
- One capability owner starts/stops camera, audio, or Display; views never own
  the SDK resource directly.
- Swift adapters may translate SDK streams into an actor-owned `AsyncStream` or
  publisher; Kotlin adapters may expose lifecycle-scoped `Flow`/`StateFlow`.
  Do not pretend these cancellation semantics are identical.
- Every frame/audio consumer has a bounded queue policy: drop, coalesce, or
  backpressure. Record why that policy is safe for the feature.
- App background, scene recreation, permission revocation, disconnect, doff,
  thermal, and stop must have an explicit transition and cleanup action.

## Test-seam matrix

| Seam | Test | Evidence label |
| --- | --- | --- |
| Domain reducer | deterministic event sequences, duplicate intents, stale epochs | build/test |
| Platform fake | adapter mapping, cancellation, error categories, fallback | fixture/build |
| DAT MockDevice | registration, permission, device, media, doff/fold, disconnect, stop | mock |
| Web simulator | 600×600 layout, focus/input, loading/error/exit | browser-sim |
| Target build | selected symbols/modules, privacy/configuration, package graph | build/static |
| Named connected pair | runtime model, firmware, companion, link, capability, operation | connected |
| Physical/release script | camera/audio/Display/input, thermal/lifecycle, signed channel | physical/signed/release-channel |

No test seam closes a higher evidence level. Record the exact source/artifact,
target, model, firmware, companion, build, and operation for connected or
physical results.

## Architecture review output

Return:

1. route and rejected adjacent surfaces;
2. module/target boundary map;
3. shared state/events and platform adapter map;
4. data-flow and on-device classification;
5. resource/concurrency/epoch rules;
6. fallback and failure matrix;
7. test/evidence ladder;
8. exact files to create/change and unresolved source/device/release gates.
