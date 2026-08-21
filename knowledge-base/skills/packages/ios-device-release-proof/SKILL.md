---
name: ios-device-release-proof
description: Plan and audit evidence for iOS permissions, entitlements, system surfaces, on-device AI, camera/sensors, Watch/CarPlay/App Clips, commerce, networking, accessibility, physical-device behavior, signing, TestFlight, and release claims. Use when deciding whether an iOS feature is actually verified, diagnosing a device-only failure, or preparing a build/release evidence report.
---

# iOS Device and Release Proof

Use this skill to separate documentation, compile, simulator, physical-device, signed-distribution, system-surface, App Store, and production evidence.

## Read before acting

- Inspect the actual `.xcodeproj`/`.xcworkspace`, scheme, target/deployment target, build settings, Info.plist, entitlements, bundle IDs, provisioning/signing, package dependencies, device family, and feature configuration.
- Read the [evidence vocabulary](../../../00-foundations/05-evidence-and-verification-language.md), [build/device/release checklist](../../../60-verification/01-build-device-and-release-checklist.md), [permission/entitlement/privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md), and [system-surface checklist](../../../60-verification/05-system-surface-checklist.md).
- Read the selected route/deep dive from the [knowledge-base map](../../../README.md) and refresh exact official Apple documentation for version-sensitive claims.

## Evidence ladder

Record each claim at the strongest level actually tested:

| Level | Can support | Cannot support by itself |
| --- | --- | --- |
| Official source | API concept, documented constraint, availability caveat | This target’s configuration, compilation, performance, permission grant, or release behavior. |
| Static inspection | Target structure, source route, plist/entitlement intent | Code compiles, signing is valid, device/service behavior, or user experience. |
| Compile/unit test | Type/API compatibility and deterministic domain logic | Camera/radio/GPU/AI quality, permissions, system UI, paired devices, APNs, thermal behavior. |
| Preview/simulator | Layout, state fixtures, template/test harness, some route callbacks | Physical sensors, hardware timing, Watch/vehicle, APNs, entitlements, battery/thermal, accessibility ergonomics. |
| Physical debug device | Permission prompts, hardware/session behavior, system surfaces, two-device interaction | Distribution signing, TestFlight/App Store configuration, production server/APNs environment. |
| Signed TestFlight/release candidate | Distribution artifact, real entitlements, store-like environment, supported device family | Production rollout, review outcome, server reliability, all regions/devices. |
| Production evidence | Live route/server/entitlement behavior for the tested environment | Universal behavior across OS versions, devices, accounts, languages, regions, or future SDKs. |

Never write “works” without naming the target, OS, device, build identity, environment, and operation that was actually tested.

## Verification workflow

1. Convert the requested claim into an observable operation: “camera frame delivered,” “Foundation Models response generated,” “HealthKit query authorized,” “Widget refreshed,” “Watch event applied,” “VoIP call reported,” “StoreKit entitlement verified,” or “signed build launched.”
2. Map the operation to required usage descriptions, capabilities, entitlements, accounts, server/APNs configuration, model/language assets, paired hardware, region, and deployment target.
3. Inspect the target artifact and source to ensure the intended bundle ID/version/build/device family and configuration are present. Treat secrets/credentials as opaque; never print them.
4. Run the smallest deterministic unit/compile/preview fixture. Capture logs/artifacts without private user data.
5. Run the real operation on the physical target; for Watch/CarPlay/communications, test every counterpart/system surface. Reset permission/account/state between cases when needed.
6. Test negative states: denied, restricted, unavailable, stale, offline, canceled, interrupted, low power, locked device, app/extension termination, server timeout, duplicate event, and migration.
7. If distributing, verify signed entitlements, provisioning, App Store/TestFlight metadata, privacy declarations, capabilities, version/build, and the release environment. Do not substitute a local archive for a submitted/reviewed/live result.
8. Report evidence and gaps in a compact matrix; do not promote an inference to proof.

## Route-specific gates

- SwiftUI/Liquid Glass: Dynamic Type, localization, VoiceOver/focus/actions, reduced motion/transparency, hit regions, contrast/legibility, adaptive layouts, and real device ergonomics.
- On-device AI: model/language availability, privacy/offline behavior, typed-output validation, prompt/tool side-effect boundaries, latency/memory/thermal measurement, fallback, and reviewable output.
- Camera/sensors/radio/GPU: usage description, capability/support check, session lifecycle, queue/backpressure/teardown, frame or sample budgets, battery/thermal, actual hardware.
- Files/photos/WebKit/PDF/extensions: user intent, security scope/bookmarks, coordinated access, data redaction, host/extension process, cancellation, provider state, and cleanup.
- Widgets/Live Activities/background: shared projection, refresh budget, stale/end state, foreground start/push environment, expiration/cancellation, no scheduling guarantee.
- Watch/CarPlay/App Clips: paired/active/reachable state, scene/category entitlement, invocation URL/AASA/App Store configuration, full-app handoff, two-device/vehicle physical testing.
- StoreKit/Apple Pay/Wallet/identity: verified transaction/server state, merchant/pass signing, nonce/state/revocation, Keychain policy, physical system UI, sandbox/TestFlight/release environment.
- CallKit/PushKit/LiveCommunicationKit: specialized push purpose, current token/APNs environment, server call reconciliation, fast system report, action fulfillment, audio/session, region/role entitlement.

## Evidence report shape

```text
Claim:
Target/scheme:
Bundle ID and version/build:
OS/device(s):
Configuration/entitlements/account/environment:
Operation exercised:
Observed result:
Artifacts/logs/screenshots:
Negative cases:
What this proves:
What it does not prove:
Next gate:
```

Do not include secrets, raw health/contact/call payloads, private tokens, or unnecessary user media in evidence. Redact screenshots and logs, and state when a result is fixture-only or preliminary API behavior.

## Related routes

- [Framework availability and device-proof matrix](../../../40-framework-routes/08-framework-availability-and-device-matrix.md)
- [Build/device/release checklist](../../../60-verification/01-build-device-and-release-checklist.md)
- [Accessibility checklist](../../../60-verification/02-accessibility-and-adaptability-checklist.md)
- [AI evaluation and safety checklist](../../../60-verification/03-ai-evaluation-and-safety-checklist.md)
- [Permission/entitlement/privacy checklist](../../../60-verification/04-permission-entitlement-and-privacy-checklist.md)
- [System-surface checklist](../../../60-verification/05-system-surface-checklist.md)
- [Availability and fallback deep dive](../../../30-on-device-ai/06-privacy-availability-and-fallback.md)

## Sources

- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Adding capabilities to your app](https://developer.apple.com/documentation/xcode/adding-capabilities-to-your-app)
- [Configuring app groups](https://developer.apple.com/documentation/xcode/configuring-app-groups)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [AVFoundation](https://developer.apple.com/documentation/avfoundation/)
- [ARKit](https://developer.apple.com/documentation/arkit)
- [Watch Connectivity](https://developer.apple.com/documentation/watchconnectivity)
- [CarPlay](https://developer.apple.com/documentation/carplay)
- [App Clips](https://developer.apple.com/documentation/appclip)
- [Background Tasks](https://developer.apple.com/documentation/backgroundtasks)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [CallKit](https://developer.apple.com/documentation/callkit)
- [PushKit](https://developer.apple.com/documentation/pushkit)
- [LiveCommunicationKit](https://developer.apple.com/documentation/livecommunicationkit)
