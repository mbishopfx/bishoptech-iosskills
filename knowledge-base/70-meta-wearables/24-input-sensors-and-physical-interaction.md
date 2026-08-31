# Input, sensors, and physical interaction

This route closes the next capability gap in the Meta Wearables team: it makes
physical input and sensors a first-class review surface without pretending that
native DAT, native Display, Web Apps, and phone APIs are interchangeable.

## Scope and source snapshot

The current public full-reference index is the DAT SDK v0.9 route for native
Android/iOS. It mentions Display buttons/taps and IMU sensors in that route.
The separate Web Apps toolkit and Developer Center route describes Web App
navigation/input plus browser motion/orientation/geolocation surfaces. The
current public DAT iOS/Android repositories expose Display UI/input guidance,
but this snapshot does not establish a dedicated public native IMU/EMG/temple
sensor API surface. The Web App toolkit is more detailed and moving; its input
and sensor guidance must remain feature-level `source-conflict`/`to-verify`
where it differs from the full-reference index.

The result is a routing contract, not a claim that every signal is available on
every pair of glasses. Use the exact package/artifact revision, firmware,
companion state, runtime capability response, and physical target evidence.

## Signal-to-surface map

| Signal or interaction | Native DAT / Display | Ray-Ban Display Web App | Phone fallback | Status in this snapshot |
| --- | --- | --- | --- | --- |
| Native Display Button/ButtonGroup/tap | Display DSL callback, selected artifact | Not the Web App API | SwiftUI/Android UI action | Source-supported Display lane; physical action still unrun |
| Captouch/D-pad focus navigation | Do not infer as a shared native event API | Toolkit guidance describes arrow-key focus navigation | Phone directional UI/VoiceOver/manual action | Web App toolkit guidance; runtime/physical gate |
| Neural Band/EMG pinch/arrow/Enter | No public native DAT symbol established here | Toolkit guidance describes semantic EMG/D-pad input | Phone button/voice/manual action | Source-supported toolkit guidance; target gate |
| Temple swipe/back | Do not infer from Web App or Display docs | Toolkit guidance describes it; full-reference conflict remains | Phone navigation/back action | `source-conflict`/`to-verify` |
| IMU/motion/orientation | Full-reference mentions IMU; exact public native symbols remain unverified | Toolkit guidance describes browser motion/orientation paths | Core Motion/Android sensor APIs | `to-verify` per surface |
| Geolocation | No native DAT glasses API established here | Toolkit guidance describes `navigator.geolocation` | Core Location/Android location | Web App source/permission/runtime gate; phone route is distinct |
| Text composer | Do not infer native DAT text input | Toolkit guidance describes it; full-reference conflict remains | Phone keyboard/voice/manual | `source-conflict`/`to-verify` |

## Native DAT and native Display rules

The public DAT Display sample uses a structured view tree with `FlexBox`,
`Button`, `ButtonGroup`, and tap callbacks. For native work:

1. Resolve the selected iOS SPM package or Android Maven artifact and inspect
   the exact Display symbols before writing the adapter.
2. Ask the runtime device whether Display is supported. A product name or a
   generation label is not a capability predicate.
3. Treat the Display view and its handlers as one session-owned surface. A
   `send`/`sendContent` replacement changes the active view and handlers; clear
   or replace it on completion, timeout, disconnect, and cancellation.
4. Normalize only the semantic action needed by the domain (`activate`,
   `back`, `next`, `previous`). Keep the native callback/source in the evidence
   record; do not make it look like a Web App keyboard event.
5. The full-reference's IMU wording is not enough to invent `MWDATMotion`,
   `MWDATSensor`, EMG, captouch, or temple-gesture symbols. Require an exact
   public reference or compile proof for the selected target.
6. If the feature truly needs motion, orientation, or location and the product
   allows phone-local sensing, use Core Motion/Core Location or Android's
   equivalent as an explicit phone fallback. Label processing location and
   consent separately.

## Web App rules

The official toolkit's current guidance describes a 600x600, focus-first input
model: arrow/D-pad movement, Enter or EMG pinch activation of the focused
element, and no default free cursor. It also describes a temple/back gesture,
standard text fields opening an on-glasses composer, and motion/orientation/GPS
sensor skills. The current full-reference index conflicts with some of these
features. Therefore:

- make every action reachable through sequential focus and a visible focus
  state;
- treat EMG/Neural Band as semantic navigation/activation until a target
  contract proves a richer stream;
- treat `DeviceMotionEvent`, `DeviceOrientationEvent`, and
  `navigator.geolocation` as browser APIs requiring secure context, permission,
  availability, bounded sampling, and teardown;
- keep Escape/back, text composition, offline cache, and extended gesture rows
  independently gated rather than bundling them into “Web App supported”;
- keep a first useful online state, unavailable state, and phone/manual route;
- validate local/browser simulator behavior, deployed HTTPS behavior, and
  physical MRBD behavior as separate evidence.

## Shared event contract

An adapter may produce this semantic event, but must retain the source-specific
record and raw data policy separately:

```text
InputEvent {
  source: display-button | dpad | emg | temple | browser-motion |
          browser-orientation | browser-geolocation | phone-sensor
  action: previous | next | left | right | activate | back | cancel | sample
  epoch: session-or-page identity
  observedAt: monotonic/local timestamp
  payload: bounded, redacted, source-specific value
  permission: granted | denied | prompt | not-required | unknown
}
```

The event owner must advance `epoch` on screen/page/session exit, disconnect,
permission denial, background/terminal state, or sensor-watch replacement. A
late callback from an old epoch is ignored. Activation/back events are
debounced by source and epoch; deliberate repeat behavior is explicit.

## Verification matrix

| Gate | What to record | Passing evidence | Common false claim |
| --- | --- | --- | --- |
| Source | URL, repository revision, package/artifact, retrieval date, access state | Current exact contract and conflicts are frozen | A concept in `llms.txt` is an importable symbol |
| Static/build | target imports, capability checks, permissions, secure context, listener ownership, privacy metadata | Selected target compiles/lints and no watcher/symbol is unowned | Native DAT and browser APIs are assumed equivalent |
| Mock/browser | duplicate, stale, denial, unsupported, stop, timeout, no-sensor, fallback | Reducer and 600x600 simulator behavior are deterministic | Simulator proves physical gesture timing |
| Connected | named account/companion/device/link/firmware/app tuple | App-visible input/capability state is recorded | Link or registration proves sensor quality |
| Physical | exact glasses, firmware, companion, app/build/channel, gesture/sensor script | Action/sensor result, latency/quality, comfort, and fallback are recorded | Gen 2/Gen 3 label generalizes to another pair |
| Release | signed artifact, channel, tester, privacy text, same critical flow | Exact signed build repeats critical behavior | Developer Mode is release proof |

## Evidence packet rows

- `INP-SOURCE-01` — freeze DAT iOS/Android, Web App toolkit, full-reference,
  target-device sources, and conflict classification.
- `INP-STATIC-01` — inspect imports, capability/permission/secure-context gates,
  lifecycle owner, privacy metadata, and processing-location declaration.
- `INP-MOCK-01` — exercise duplicate, stale, unsupported, denied, stop, and
  fallback events through a deterministic fixture.
- `INP-BROWSER-01` — run the Web App simulator and deployed HTTPS page at 600x600
  for focus/input/sensor availability and fallback.
- `INP-CONNECTED-01` — record the named companion/device/link tuple and
  app-visible capability/input state.
- `INP-PHYSICAL-01` — run the exact interaction/sensor script on named glasses
  and record the physical result rather than a generation inference.
- `INP-RECOVERY-01` — deny permission, disconnect, inject a stale event, stop a
  sensor watch, recover once, advance the epoch, and repeat the original action.
- `INP-RELEASE-01` — repeat the critical input/sensor flow with the signed
  release-channel build and privacy/fallback surfaces.

## Handoff checklist

- [ ] Product surface and exact signal source are named.
- [ ] Native DAT, native Display, Web App, and phone fallback boundaries are
  explicit.
- [ ] Every target capability is source-backed or marked `to-verify`.
- [ ] Input/sensor events carry source and epoch; teardown is owned.
- [ ] Raw trace, precise location, retention, and processing location are
  documented.
- [ ] Denial, no-sensor, stale, duplicate, disconnect, timeout, and fallback
  fixtures exist.
- [ ] Browser/MockDevice, connected, physical, signed, and release results are
  kept in separate evidence classes.
- [ ] Gen 2/Gen 3 wording uses exact model/capability/firmware evidence.

## Sources

- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS Display Access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT Android Display Access skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/display-access/SKILL.md)
- [Meta Wearables Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Web App agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Web App Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
- [Apple Core Motion](https://developer.apple.com/documentation/coremotion)
- [Apple Core Location](https://developer.apple.com/documentation/corelocation)
