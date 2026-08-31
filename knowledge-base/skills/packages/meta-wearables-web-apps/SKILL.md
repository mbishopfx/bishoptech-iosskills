---
name: meta-wearables-web-apps
description: Build and review Meta Wearables Web Apps for the Ray-Ban Display with the official HTML/CSS/JavaScript route, 600×600 display contract, public HTTPS delivery, focus and D-pad/EMG input, performance limits, source-conflict handling, and separate simulator/physical-device evidence.
---

# Meta Wearables Web Apps

Use the official Web App surface when the experience should be delivered to the Meta Ray-Ban Display as a web page. Keep it separate from a native iOS DAT companion app and from native DAT Display code.

## Read before acting

- Inspect the actual Web App source, build toolchain, URL/deployment target, assets, state model, and any companion phone integration.
- Read [Web Apps, Display, and input](../../../70-meta-wearables/06-web-apps-display-and-input.md) and the local [Web App display contract](references/display-contract.md).
- Load the Web Apps `api_surface.rows` from the portable [source-pinned manifest](../../../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
  and preserve each runtime/source-conflict row independently; toolkit guidance
  is not physical glasses proof.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) and the local [input/sensor contract](../meta-wearables-input-sensors/references/input-sensor-contract.md) when the feature uses D-pad/EMG/temple input, motion, orientation, geolocation, or source-conflicted Web App features.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) for public-data boundaries, processing location, network/storage behavior, and typed fallback.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) for HTTPS origin/deployment boundaries, client-visible assets, server-side credentials, Meta AI add/launch state, and any claim that a Web App has native DAT attestation or local processing.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) for companion, firmware, public HTTPS launch, Display provisioning, release-channel, and recovery gates.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) when a Web App shares product state, data, or fallback behavior with a native companion.
- Read the portable [toolkit skill map](references/toolkit-skill-map.md) when the request asks for scaffolding, text entry, gestures, sensors, offline behavior, API connection, staging, or publishing.
- For a new reducer-first scaffold, copy the [dependency-free Web App starter](../meta-wearables-implementation-recipes/assets/meta-wearables-web-starter/) and run `node --test ../meta-wearables-implementation-recipes/assets/meta-wearables-web-starter/test/display-state.test.mjs` from this package directory before binding the selected toolkit revision.
- Read the official [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp), [agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md), [Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md), and [performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md).
- Run the bundled [Web App preflight receipt runner](scripts/run_webapp_preflight.py) against the actual entrypoint before calling a local HTML/JS surface a Meta delivery target. Use `--require-meta-markers` and, when a public URL is available, `--origin <https-url> --check-origin --require-https-origin`; this keeps hosted HTTPS evidence separate from browser-simulator and physical Display evidence.
- Compare the toolkit `main` guidance with the current [full Developer Center reference](https://wearables.developer.meta.com/llms.txt?full=true). The reviewed sources conflict about text composition, offline support, back navigation, sensors, and extended gestures; carry those features as `source-conflict`/`to-verify` until the exact runtime closes the gap.
- Refresh the current [Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps) and record any login/access limitation rather than treating an inaccessible page as proof.

## Fast path

Preflight the entrypoint and public origin first, then build one 600x600 interaction with keyboard/focus/input and fallback states. Validate the local fixture, HTTPS origin, browser simulator, and physical Display in order, stopping at the first unavailable gate.

## Web App workflow

1. Define the glanceable user outcome and whether the Web App is standalone or paired with a phone service.
2. Build the smallest HTML/CSS/JS surface within the official display contract: 600×600, additive content, short text, clear hierarchy, and no assumptions about a phone viewport. Keep source-conflicted features behind explicit capability/fallback decisions.
3. Implement focus and input deliberately. The user should know the focused item, the D-pad/available input actions, the selected result, and how to dismiss or recover.
4. Use the current official metadata/launch contract and a public HTTPS URL. Do not ship a local URL, private tunnel, environment-secret URL, or native DAT import inside a Web App.
5. Keep data minimal and resilient. Design loading, stale data, no connection, permission/consent handoff, invalid input, and service failure states.
6. Follow the official performance guidance: keep bundles and assets small, minimize work per update, avoid unnecessary animation, and measure load/interaction latency on the target surface.
7. Test in the official browser simulator, then validate the deployed URL, then run the same script on physical Ray-Ban Display hardware. Record each result separately.

## Source-conflict handling

The public full-reference index reviewed 2026-08-22 says Web Apps do not
support camera, microphone, text input, offline support, notifications, or back
navigation. The official toolkit `main` at commit
The 2026-08-30 source refresh confirmed that the toolkit moved from
`facebookincubator/meta-wearables-webapp` to `facebook/meta-wearables-webapp`.
The relocation compare changed README, installer, and plugin metadata only; it
did not add a runtime/API proof row. The current toolkit commit
`a2714f862c61b1ce9c6cb624fc7e4938087102db` documents an on-glasses
handwriting/voice composer, service-worker/offline patterns, Escape/back,
gestures, and sensors. Do not collapse those into a single “supported” list.

For each conflicted feature, record the source revision, exact simulator/build,
target firmware, physical result, fallback, and release decision. The safest
implementation keeps phone/manual entry and online/error/exit fallbacks until
the runtime result and current authenticated docs agree.

## Display contract

- 600×600 is the Web App canvas contract; design inside it rather than scaling a phone page down.
- Content is additive to the Display experience; preserve legibility and avoid visual noise.
- D-pad/EMG or other current input must have a visible focus and deterministic action mapping.
- Every screen has a first useful state and a recoverable unavailable/error state.
- The app must tolerate missing, stale, or delayed data without exposing private implementation details.
- Text composer, offline cache, Escape/back, extended gestures, and sensors are source-conflict features in the current public snapshot; gate them independently.

## Required output

- route decision: Web App versus native DAT Display;
- public URL/launch metadata and deployment verification;
- display/input state map and performance budget;
- simulator test cases;
- physical Ray-Ban Display test script and evidence status;
- phone handoff, privacy, and failure behavior.

## Hard boundaries

- A browser simulator proves web behavior and some input logic; it does not prove real glasses rendering, brightness, latency, comfort, or hardware input.
- Do not claim support for Oakley, “Gen 3,” or any other device without a current official Web App/device mapping and hardware result.
- Do not expose secrets or raw personal media in a public URL or client bundle.
- Do not represent a Web App as a native iOS DAT integration in App Store copy or source documentation.
- Do not assume arbitrary browser APIs, background execution, camera/microphone access, notifications, or Meta AI voice commands are available on the Display. Treat the toolkit’s text/offline/back/sensor/gesture guidance as target-specific until proven.

## Related routes

- [Meta route planner](../meta-wearables-route-planner/SKILL.md)
- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Web App preflight receipt runner](scripts/run_webapp_preflight.py)

## Sources

- [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp)
- [Web App agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Web App Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Web App performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
- [Official Ray-Ban Display Web App simulator](https://chromewebstore.google.com/detail/meta-ray-ban-display-web/jpjlmmodokemlepklkdbimceggpbjcll)
