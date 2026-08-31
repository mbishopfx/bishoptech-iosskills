# Web App display and input contract

Use this as a compact review fixture. The official Web App repository and
Developer Center remain authoritative when a detail changes, but the current
public snapshots contain a capability conflict that must be recorded rather
than silently resolved.

## Source conflict

- The full Developer Center index reviewed 2026-08-22 lists no camera,
  microphone, text input, offline support, notifications, or back navigation.
- The Web App toolkit `main` at commit
  `a2714f862c61b1ce9c6cb624fc7e4938087102db` (the canonical repository after
  the 2026-08-30 facebookincubator-to-facebook move) documents text composition,
  service-worker/offline patterns, Escape/back behavior, extended gestures, and
  Generic Sensor API guidance.

Mark text composer, offline, back, extended gestures, and sensors
`source-conflict`/`to-verify` until the exact Developer Center/MCP result,
simulator, firmware, and physical MRBD run agree. Keep a phone/manual fallback.

## Layout

- Treat the Ray-Ban Display Web App surface as a 600×600 canvas.
- Keep content additive, high-contrast, glanceable, and bounded; a phone layout scaled into the canvas is not a design review pass.
- Establish a visual hierarchy for current state, primary action, secondary action, and unavailable/error state.
- Test long text, no data, loading, stale data, and a disconnected companion service.

## Input

- Every interactive element has a deterministic focus order.
- Focus is visible without relying on color alone.
- D-pad/available input directions map to actions that are documented in the UI or product behavior.
- Selection, back/dismiss, timeout, and loss of focus return to a known state.
- Test the toolkit-described HTML-field composer, Escape/back, offline cache,
  sensors, and opt-in gestures only as explicit `to-verify` rows; do not count
  their presence in a desktop browser as glasses support.
- Do not assume touch, arbitrary keyboard events, EMG gestures, voice commands, or browser APIs unless the current official route documents them.

## Delivery

- public HTTPS URL;
- launch/metadata contract from the current Web App docs;
- no secrets in client assets;
- cache and loading behavior measured on the target route;
- source-conflicted features have an explicit fallback and evidence row;
- simulator URL test followed by deployed URL test;
- physical Display result recorded with model and firmware.

## Review questions

1. Can the user understand the state in one glance?
2. Can the user move focus and select/dismiss without ambiguity?
3. What happens when the phone service is unavailable?
4. What is the smallest data sent to the page?
5. Which observation is simulator-only, and which has physical proof?

## Sources

- [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp)
- [Web App Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Web App performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
