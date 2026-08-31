---
name: meta-dat-display
description: Design and implement native Meta DAT Display surfaces with capability gating, compact glanceable state, ButtonGroup/input handling, clear teardown, phone handoff, and physical Ray-Ban Display evidence. Use for native glasses UI requests, not for Web App HTML surfaces.
---

# Meta DAT Display

Design the glasses surface as a small, stateful system surface. The phone remains the configuration, consent, recovery, and detailed-content surface unless the product has a proven reason to move that work onto the Display.

## Read before acting

- Inspect the actual DAT version, target device family, connected-model assumptions, phone UI, lifecycle, and any existing Display adapter.
- Read [Display access and glasses UI](../../../70-meta-wearables/04-display-access-and-glasses-ui.md), [device models and capability matrix](../../../70-meta-wearables/05-device-models-and-capability-matrix.md), and [mock evidence](../../../70-meta-wearables/07-mockdevice-testing-and-evidence.md).
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) before sharing Display actions with Web App D-pad/EMG/temple input or claiming a native sensor API.
- Read the [DAT iOS API surface atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md) for the release-anchored Display module, capability, ButtonGroup, video, and teardown map.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) for sanitized Display payloads, phone handoff, stale data, lifecycle, thermal, and fallback claims.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when Display delivery depends on mobile identity, callbacks, Developer Mode/release attestation, credential redaction, or a privacy/review claim.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) for firmware, companion, on-glasses DAT-app provisioning, Display update-required errors, release-channel, thermal, and recovery behavior.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) before sharing Display state with SwiftUI, Android, or a Web App.
- Refresh the official [DAT iOS Display skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/display-access), [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), and current [Display documentation](https://wearables.developer.meta.com/docs/develop/).
- Keep this route separate from [Meta Wearables Web Apps](../meta-wearables-web-apps/SKILL.md); native DAT Display and a 600×600 Web App have different APIs and proof.

## Display workflow

1. Ask the runtime device whether it supports Display. Use the current capability API, including `DeviceType.supportsDisplay()` where exposed by the selected release; do not infer capability from a product name.
2. Define a compact display state machine: `hidden`, `presenting`, `focused`, `actionAvailable`, `dismissed`, `timedOut`, `disconnected`, and `unsupported` as appropriate.
3. Build one clear root Display view for the feature and keep its content legible at a glance. Prefer one primary status or action over a miniature phone screen.
4. Use the current Display input contract, including ButtonGroup/action handling where the installed SDK exposes it. Model focus, selection, previous/next, dismiss, timeout, and accidental input.
5. Keep the source of truth in the phone app/domain layer. Project a small, sanitized snapshot onto the Display and define behavior when that snapshot is stale.
6. Clear or replace the Display on completion, cancellation, disconnect, and route change using the current API (for example, `Display.clearDisplay()` where available).
7. Test the Display content with supported and unsupported models, no connection, long text, dynamic state, low confidence, and a lost phone session.

## Interaction and visual contract

- one glance should explain what changed and what action is possible;
- high contrast, short labels, stable focus, and predictable action order;
- no private content, sensitive transcription, or raw media unless the product has explicitly designed and disclosed it;
- every glasses action has a phone fallback and a recoverable error state;
- no assumptions about color, brightness, input, or rendering resolution beyond the current official device documentation.

## Fast path

Start with a capability gate, one compact Display state, one input event, and teardown. Validate the mock/render contract and phone fallback before adding rich layout, media, or repeated updates.

## Required output

- exact target model and capability gate;
- Display state machine and phone handoff;
- view/input ownership and teardown behavior;
- mock/simulator test fixture;
- physical Display test script with expected observations;
- unsupported and disconnected fallback.

## Hard boundaries

- `supportsDisplay()` is a gate, not proof that a particular product-generation label is supported.
- A mock Display or screenshot proves layout logic only; it does not prove brightness, focus, D-pad/button behavior, latency, or comfort on glasses.
- Do not use the native Display route for a Web App request or vice versa.
- Do not claim “Gen 3 Display” until the exact model and current SDK mapping are sourced and observed.

## Related routes

- [Meta route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [SwiftUI native design](../swiftui-native-design/SKILL.md)

## Sources

- [Meta DAT iOS Display access skill](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills/display-access)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Meta Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Apple accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
