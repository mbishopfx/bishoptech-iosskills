# Input and sensor contract

This is the portable review contract for physical input and sensor work. It is
deliberately more conservative than a product brief: a symbol, permission, or
gesture is not considered available until the selected source and runtime prove
it.

## Capability ledger

| Surface | Signal | Public snapshot | Implementation rule | Proof still required |
| --- | --- | --- | --- | --- |
| Native DAT Display | `Button`, `ButtonGroup`, `FlexBox.onTap` | Source-supported in current iOS/Android Display guidance and samples | Use the selected artifact's exact callback API; clear/replace views and gate capability | Named Display-capable glasses with action/focus/timeout/disconnect result |
| Native DAT | IMU or other glasses sensors | Full-reference index mentions IMU sensors; current public iOS/Android role trees do not expose a dedicated sensor lane in this snapshot | Keep exact native sensor symbols `to-verify`; do not substitute phone sensors silently | Authenticated API/reference or selected artifact compile plus named-device output |
| Web App | D-pad/captouch and EMG/Neural Band semantic input | Toolkit guidance describes arrow focus movement and Enter/activation of the focused element | Focus all actions; do not use a free cursor by default | Browser simulator, deployed HTTPS URL, and physical MRBD input run |
| Web App | temple/back gesture and Escape | Toolkit guidance describes back behavior; full-reference index conflicts on Web App back support | Gate independently; keep an explicit exit/phone fallback | Target runtime and physical MRBD result |
| Web App | motion/orientation/geolocation | Toolkit guidance describes browser sensor paths; full-reference index and runtime availability require reconciliation | Secure-context/permission/feature checks, bounded sampling, cleanup, demo fallback | Simulator/API result, deployed URL, target firmware, and physical sensor run |
| Phone fallback | Core Motion, Core Location, Android sensors/location | Platform APIs, not Meta glasses capability | Label the signal as phone-local and disclose location/processing separately | Target phone build/device and user permission result |

## Normalized event shape

Adapters may normalize into this shape, but the source-specific record must be
retained alongside it:

```text
InputEvent {
  source: display-button | dpad | emg | temple | browser-motion |
          browser-orientation | browser-geolocation | phone-sensor
  action: previous | next | left | right | activate | back | cancel | sample
  epoch: session-or-page identity
  observedAt: monotonic/local timestamp
  payload: bounded source-specific value
  permission: granted | denied | prompt | not-required | unknown
}
```

`epoch` is mandatory for any event that can outlive a screen, session, page,
device link, or sensor watch. `payload` must not become a raw trace by default.

## Lifecycle invariants

1. Register input/sensor listeners only after the owning surface and capability
   are ready.
2. Store listener/watch handles with the surface/session owner.
3. On screen exit, session stop, disconnect, background, permission denial,
   timeout, or unsupported result, stop the handle and advance the epoch.
4. Ignore events with a prior epoch or an unknown source.
5. Debounce duplicate activate/back events by source and epoch; preserve a
   deliberate repeat action through an explicit repeat policy.
6. Bound sensor frequency, precision, storage, and network transmission.
7. Return a visible unavailable/permission/fallback state rather than leaving
   a focused control or sensor consumer waiting forever.

## Source-conflict procedure

When the official sources disagree:

- record the URL, revision, retrieval date, and exact feature wording;
- classify the feature as `source-conflict` and implementation status as
  `to-verify`;
- implement the smallest fallback that does not depend on the conflict;
- run browser simulator/compile checks only as their own evidence classes;
- close the row only after the selected runtime and named physical target agree;
- preserve the conflict history in the Meta source registry and freshness log.

## Privacy and safety review

- Sensor access and location access are separate user-consent decisions.
- Do not send raw IMU/EMG traces or precise location to a remote service unless
  the product has a specific purpose, disclosure, retention, deletion, and
  security control.
- A local callback or browser event does not prove where downstream inference
  runs. Record processing location as `glasses-native`, `phone-local`,
  `remote`, `mixed`, or `unknown`.
- Model how high-frequency sampling affects battery, thermal state, radio use,
  and user comfort. Stop or reduce sampling when the surface is hidden or the
  user leaves the flow.
- Make the phone fallback clear when a gesture, sensor, permission, connection,
  or target firmware is unavailable.

## Evidence rows

| ID | Minimum evidence | Pass condition | Never infer |
| --- | --- | --- | --- |
| `INP-SOURCE-01` | Current DAT iOS/Android, Web App toolkit, full-reference, and target-device source snapshot | Source revision and conflict status are recorded | Current physical support |
| `INP-STATIC-01` | Target imports, capability gates, permissions/secure context, listener ownership, privacy metadata | No unsupported symbol or unowned watcher remains | Runtime sensor quality |
| `INP-MOCK-01` | Mock/reducer fixtures for duplicate, stale, denial, unsupported, stop, and fallback | Deterministic state transitions pass | Glasses gesture recognition |
| `INP-BROWSER-01` | Web App simulator and deployed HTTPS input/sensor checks | Focus/action and fallback behavior are recorded at 600x600 | Physical MRBD timing or comfort |
| `INP-CONNECTED-01` | Named companion/device/link with app-visible capability/input state | The exact connected tuple is recorded | Physical sensor quality |
| `INP-PHYSICAL-01` | Named glasses, firmware, companion, app/build/channel, exact gesture/sensor script | Input/sensor result, latency/quality notes, and fallback are recorded | Neighboring generation support |
| `INP-RECOVERY-01` | Permission denial, disconnect, stale event, sensor stop, and one least-invasive recovery | Original action is retried under a new epoch and result recorded | A retry loop or source note |
| `INP-RELEASE-01` | Signed/release-channel build and target tuple | Critical input/sensor flow and privacy/fallback behavior repeat | Developer Mode or debug build as release proof |
