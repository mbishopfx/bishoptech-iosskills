---
name: meta-wearables-input-sensors
description: Design and verify Meta Wearables physical input and sensor experiences across native DAT Display, Ray-Ban Display Web Apps, and phone fallbacks, while keeping hardware signals, browser APIs, permissions, lifecycle, and physical-device evidence separate.
---

# Meta Wearables input and sensors

Use this role whenever a Meta Wearables experience depends on a wearer gesture,
Display button, Neural Band/EMG action, temple/captouch input, inertial data,
orientation, or geolocation. It keeps the event source and evidence level
explicit so an agent does not turn a Web App browser API or a Display callback
into a cross-platform native DAT promise.

## Read before acting

- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) and the [input/sensor contract](references/input-sensor-contract.md).
- Read [Display Access](../../../70-meta-wearables/04-display-access-and-glasses-ui.md) for native DAT Display capability, compact UI, ButtonGroup/action callbacks, and teardown.
- Read [Web Apps display and input](../../../70-meta-wearables/06-web-apps-display-and-input.md) and the official [Web App Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md) for the 600x600 focus/D-pad/EMG surface.
- Read [device models and capability matrix](../../../70-meta-wearables/05-device-models-and-capability-matrix.md) and [device-generation/runtime support](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) before using Gen 2, Display, or Gen 3 language.
- Read [on-device compliance](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) for sensor processing location, raw-data retention, consent, thermal, and fallback decisions.
- Read [transport and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) for link loss, stale events, disconnect, and recovery.
- Read [device and release evidence](../../../70-meta-wearables/12-device-and-release-evidence-packet.md) before calling input or sensor behavior connected, physical, signed, or released.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp), and [full platform reference](https://wearables.developer.meta.com/llms.txt?full=true) for version-sensitive claims.

## Route the signal before writing code

1. Name the product surface: native DAT companion, native DAT Display, Ray-Ban Display Web App, or phone/system fallback.
2. Name the signal source: native Display tap/ButtonGroup callback, Web App keyboard/focus event, captouch/D-pad, Neural Band/EMG, temple gesture, browser motion/orientation/geolocation API, or an ordinary phone sensor.
3. Resolve the target through runtime capability metadata and the exact firmware/app/package revision. Do not use a consumer label as a capability predicate.
4. Define the event contract before the reducer: source, timestamp/epoch, semantic action, payload bounds, permission state, stale/disconnect behavior, and cancellation.
5. Keep source-conflicted Web App features independently gated. The reviewed full-reference index and the moving Web App toolkit do not agree on text composition, offline behavior, back navigation, sensors, or extended gestures.
6. Provide a phone/manual fallback for every action that can strand the wearer, and record whether the fallback is local, remote, or unavailable.

## Native DAT Display lane

- Use the selected DAT release's public Display DSL and callback surface. The
  current public samples show `ButtonGroup`, `Button`, and `FlexBox.onTap`; they
  do not establish a separate public iOS/Android sensor module for IMU, EMG, or
  temple gestures.
- Treat Display tap/back behavior as a Display interaction contract, not as a
  general event bus shared with Web Apps.
- Gate Display with the runtime capability predicate exposed by the selected
  artifact, clear/replace the active view on terminal paths, and ignore events
  from an old session epoch.
- If the current selected artifact or authenticated reference exposes a native
  IMU/sensor API, add it as a versioned adapter with exact symbols and tests. If
  it does not, keep the native sensor row `to-verify` and use the phone sensor
  route only when the product explicitly permits that substitution.

## Ray-Ban Display Web App lane

- Build focus-first UI. The official toolkit guidance describes D-pad/captouch
  arrow movement, Enter/EMG activation of the focused element, and Escape/back
  or a back gesture as target behavior; the full-reference index marks several
  Web App capabilities differently, so record the exact source and runtime.
- Treat Neural Band/EMG as semantic navigation/activation input unless the
  target-specific contract proves a richer gesture stream. Do not make a
  positioned cursor or continuous drag the default.
- Gate motion/orientation/geolocation with secure-context, permission, feature,
  availability, and cleanup checks. Use a demo or phone fallback when a sensor
  is absent or denied.
- Keep browser sensor events out of a native DAT adapter. A Web App can be
  hosted on HTTPS and still lack the same capability on a particular firmware,
  account, or release channel.

## Event contract and test loop

Use a small normalized event model, for example:

```text
InputEvent {
  source: display-button | dpad | emg | temple | browser-motion |
          browser-orientation | browser-geolocation | phone-sensor
  action: previous | next | left | right | activate | back | cancel | sample
  epoch: session-or-page identity
  observedAt: monotonic/local timestamp
  payload: bounded, redacted, source-specific value
}
```

The implementation must:

- reject events from an old session/page epoch;
- debounce duplicate activations without swallowing deliberate repeats;
- stop listeners and sensor watches on screen exit, permission denial,
  disconnect, background, and terminal session states;
- surface permission, unsupported, unavailable, stale, and timeout states;
- avoid logging raw sensor traces, precise location, identifiers, or personal
  gesture data unless the product has a documented reason and retention rule;
- test denial, no sensor, duplicate event, stale event, teardown, and phone
  fallback before a physical run.

## Fast path

Route each signal by source and host first: native Display, Web App, glasses sensor, or phone sensor. For one signal, define epoch, lifecycle, permission, and one reducer event; test duplicate, out-of-order, and disconnect behavior before adding physical-input proof.

## Required output

- route and exact signal-source decision;
- capability/permission/secure-context matrix with unresolved rows;
- normalized input/sensor event contract and lifecycle owner;
- native DAT/Web App/phone adapter boundary;
- mock/browser fixture and physical named-target script;
- privacy, retention, thermal, and fallback notes;
- evidence rows `INP-SOURCE-01`, `INP-STATIC-01`, `INP-MOCK-01`,
  `INP-BROWSER-01`, `INP-CONNECTED-01`, `INP-PHYSICAL-01`,
  `INP-RECOVERY-01`, and `INP-RELEASE-01` with status.

## Hard boundaries

- Do not claim native DAT IMU, EMG, Neural Band, temple-gesture, or geolocation
  APIs from a conceptual full-reference label alone.
- Do not claim a Web App sensor or composer feature is supported because a
  browser or toolkit source mentions it; reconcile the current reference,
  simulator, target firmware, and physical result.
- Do not map Gen 2 or user-called Gen 3 to a sensor/input capability without an
  exact model, runtime capability response, and named hardware result.
- Do not collect or retain raw IMU, EMG, gesture, or precise-location traces by
  default. Sensor availability is not consent, and on-device capture is not
  proof of on-device processing.
- Browser simulation, MockDevice, a compile, or a connected link is not proof
  of physical input timing, comfort, gesture recognition, sensor quality, or
  release behavior.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Transport and reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)

## Sources

- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT iOS Display access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT Android Display access skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/display-access/SKILL.md)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Web Apps agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Web Apps Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
