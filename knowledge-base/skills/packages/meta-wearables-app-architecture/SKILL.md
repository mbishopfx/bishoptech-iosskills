---
name: meta-wearables-app-architecture
description: Architect maintainable iOS, Android, and Ray-Ban Display applications on top of Meta Wearables DAT without leaking platform SDKs into UI or domain code. Use when starting a wearable app, adding camera/audio/Display/Web App capabilities, sharing behavior across Swift and Kotlin, designing phone-first fallbacks, or turning a DAT feature plan into adapters, state machines, test seams, and release-ready modules.
---

# Meta Wearables application architecture

Design the product boundary before importing DAT symbols. Keep shared product
intent, state, policy, and fallback behavior separate from platform-specific
Swift, Kotlin, and Web App adapters. The architecture must remain useful when
glasses are absent, unsupported, disconnected, permission-denied, thermally
limited, or on a different model.

## Read before acting

- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md), [route-selection page](../../../70-meta-wearables/00-platform-and-route-selection.md), [full-SDK matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), and [on-device contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md).
- Load the [vertical-slice playbooks](references/vertical-slice-playbooks.md) after filtering the source-pinned API register; choose the smallest playbook that matches the outcome and carry its row IDs, state machine, fallback, and proof ladder into the handoff.
- Load the [implementation recipes](../meta-wearables-implementation-recipes/SKILL.md) when the request needs Swift, Kotlin/Java, or Web App scaffolding; preserve compile-gated signatures and adapter boundaries.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) before placing identity, callback, credential, attestation, Web App origin, or processing-location state in shared product architecture.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) before sharing Display, Web App, or phone-sensor events; preserve source, epoch, teardown, and fallback boundaries.
- Read the [DAT iOS foundations](../../../70-meta-wearables/01-dat-ios-sdk-foundations.md), [Android parity route](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md), [device/release packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md), and [operational recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md).
- Inspect the real target, package/artifact graph, deployment/min SDK, permissions, privacy metadata, lifecycle, existing media/display adapters, and Web App deployment boundary.
- Refresh the selected [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp), and [full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat) before using a version-sensitive symbol.

## Architecture workflow

1. **Freeze the product contract.** Name the user outcome, primary surface,
   phone fallback, requested capabilities, target labels, exact evidence level,
   processing location, and highest-consequence failure.
2. **Choose boundaries.** Create a shared domain/policy layer, a platform
   adapter layer, surface presenters, and test fakes. Keep iOS DAT, Android
   DAT, native Display, and Web Apps as distinct adapters—not a single
   cross-platform SDK facade that hides incompatible semantics.
3. **Model state before effects.** Define registration, permission, device
   selection, session, capability, transport, thermal, cancellation, and
   fallback states. Make one owner reduce SDK events into app state; views only
   render state and send user intents.
4. **Define capability seams.** Use product-level protocols/interfaces for the
   requested operation, then implement them in Swift, Kotlin, or Web App code.
   Keep exact DAT imports, `AsyncSequence`/publisher details, `Flow`/
   `StateFlow`, `DatResult`, and Web APIs inside the adapter.
5. **Control concurrency and resources.** Give each session/capability an
   ownership boundary, cancellation token or coroutine scope, event epoch, and
   terminal stop path. Bound camera/audio work and never let stale frames or
   Display actions cross a new session epoch.
6. **Design the data path.** Label every frame, audio sample, transcript,
   sensor value, Display payload, identifier, model result, network request,
   cache, and log as glasses-native, phone-local, remote, mixed, or unknown.
   Apply consent, retention, thermal, and deletion rules at the boundary.
7. **Build the fallback first.** The phone route must remain useful with no
   companion, no glasses, no Display capability, no permission, no network,
   stale data, or a terminal session error. Fallback is typed product state,
   not a hidden retry spinner.
8. **Test each seam.** Run pure reducer/domain tests, adapter fakes, DAT
   MockDevice, Web App browser simulation, target build, connected-device, and
   physical scripts as separate evidence levels.
9. **Audit release architecture.** Verify target configuration, privacy,
   signing, companion/account/channel, firmware, on-glasses DAT app, and the
   exact build before calling the architecture releasable.
10. **Select a vertical slice.** Use the native Display, camera-to-phone,
    audio-first, Web App, or shared-outcome playbook; do not invent a broad
    cross-platform facade when a capability-specific adapter is required.

## Fast path

Draw four boxes before writing adapters: shared domain, platform adapter, surface presenter, and test fake. Choose one playbook, reject any interface that leaks SDK types, and implement one reducer/fake plus one adapter method and typed fallback before pursuing cross-platform parity.

## Required output

- surface and route decision with rejected alternatives;
- selected vertical-slice playbook and manifest/evidence row IDs;
- selected implementation recipe, confirmed versus `to-verify` symbols, and next compile task;
- module/target boundary diagram and ownership table;
- shared domain state machine and platform adapter interfaces;
- iOS, Android, and Web App implementation mapping with exact symbols marked
  `source`, `compile`, or `to-verify`;
- data-flow, privacy, thermal, lifecycle, and fallback contract;
- concurrency/resource ownership and stale-event strategy;
- reducer/fake/MockDevice/browser/connected/physical test seams;
- package, account, firmware, channel, signing, and release gates;
- files/modules to create or change and the next evidence task.

## Hard boundaries

- Never place DAT imports, Meta AI registration, or Web App browser APIs in a
  SwiftUI/Compose view or shared domain model.
- Never translate Swift symbols into Kotlin or Web APIs by naming similarity;
  the selected artifact and target compile decide the adapter surface.
- Never hide camera, audio, Display, sensor, or remote-processing failure behind
  an unbounded retry or a generic `isLoading` state.
- Never treat one “common” interface as proof of cross-platform parity. Return
  capability-specific unsupported/to-verify states where a platform differs.
- Never call a phone-local fallback glasses-native or call a Web App a native
  DAT module.
- Never use a compile, fake, MockDevice, browser simulator, or shared reducer
  test as proof of physical glasses behavior.
- Never map “Gen 3” to an enum or adapter until official mapping and named
  runtime evidence exist.
- Never put tokens, serials, raw media, transcripts, or private diagnostics in
  source, fixtures, logs, or skill archives.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [Full-SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Camera/audio](../meta-dat-camera-audio/SKILL.md)
- [Native Display](../meta-dat-display/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Vertical-slice playbooks](references/vertical-slice-playbooks.md)
- [Implementation recipes](../meta-wearables-implementation-recipes/SKILL.md)

## Sources

- [Application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Portable vertical-slice playbooks](references/vertical-slice-playbooks.md)
