# Research log

## 2026-09-14 iOS 27 SwiftUI and SDK source refresh

- Rechecked Apple’s [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes), [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes), and [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/).
- Added the [iOS 27 SwiftUI and SDK refresh](../knowledge-base/10-swiftui/13-ios27-swiftui-refresh.md) and source-refresh package reference covering toolbar overflow/minimization, `Document`/`ReadableDocument`/`WritableDocument`, reorderable containers, `swipeActionsContainer`, `AsyncImage` caching/session control, interactive text selection, macro-backed `@State`, and the `MetricManager` async-sequence route.
- Updated the Apple package/index titles and cross-cutting route language to treat iOS 27/Xcode 27 as the current documentation lane while preserving iOS 26 compatibility and historical claims. The current `xcode-select` exposes Xcode 27.0, the iOS 27.0 SDK, and Swift 6.4 for a targeted symbol-level type-check; Xcode 26.4 remains the explicit earlier-toolchain fallback.
- Added reusable [iOS 27 native design](../knowledge-base/90-templates/ios27-native-design-brief.md) and [performance/on-device proof](../knowledge-base/90-templates/ios27-performance-and-on-device-proof.md) templates, plus the HIG platform/resource matrix. They explicitly separate Liquid Glass’s functional depth from content/decorative layers and separate SDK compile evidence from runtime/device/performance claims.
- The available simulator runtime is iOS 26.4; app-target build, iOS 27 simulator, physical-device, archive, TestFlight, App Store, and production evidence remain open gates.

The README is the visual entry point. This page keeps the expansion record discoverable without turning the project homepage into a changelog.

## Current state

The knowledge base is organized around a source-and-evidence contract: choose the capability, verify target and availability gates, design the native surface, implement the smallest route, and collect the evidence that the claim actually requires.

The active research lanes include:

- SwiftUI composition, state, navigation, controls, accessibility, alternate input, scenes, media, charts, layout, scrolling, focus, rich text, and visual export.
- Liquid Glass composition, interaction states, safe-area placement, legibility, reduced-effects fallback, adaptive layouts, and native-design verification.
- Apple Intelligence, Foundation Models, Core ML, Vision, Natural Language, Speech, Translation, structured proposals, evaluation fixtures, model readiness, privacy, refusal, and deterministic commit boundaries.
- Apple services and system surfaces including SwiftData, CloudKit, HealthKit, Contacts, EventKit, WeatherKit, HomeKit, Bluetooth, Nearby Interaction, Network, widgets, Live Activities, App Intents, extensions, background work, and document providers.
- Media, spatial, and physical-input routes including AVFoundation, MusicKit, ShazamKit, NFC, ARKit, RealityKit, Metal, SpriteKit, GameKit, haptics, camera, microphone, sensors, and companion devices.
- Identity, commerce, and release work including StoreKit, PassKit, Wallet, Apple Pay, Sign in with Apple, passkeys, Keychain, CryptoKit, privacy manifests, performance, signing, TestFlight, and App Store evidence.

## Expansion record

The source-linked route work is intentionally cumulative. Each expansion adds API selection, target and availability gates, lifecycle ownership, privacy/configuration boundaries, AI review limits where relevant, and a proof matrix. The complete source material lives in [the knowledge-base map](../knowledge-base/README.md), [the coverage matrix](../knowledge-base/coverage-matrix.md), and [the official source registry](../knowledge-base/sources/official-source-registry.md).

The current public bundle includes nineteen Apple role packages and twenty-three Meta Wearables extension role packages listed in the [skills catalog](skills-catalog.md), plus portable `.skill` archives in [knowledge-base/skills/dist](../knowledge-base/skills/dist).

The Meta Wearables extension adds 30 source-linked route pages and twenty-three role packages for DAT iOS/Android, dedicated platform API atlases, the public plugin/API/tooling surface, a portable source-pinned surface manifest, full-SDK capability auditing, native Display and physical input/sensor semantics, security/attestation and credential boundaries, version/device compatibility, Ray-Ban Display Web Apps, camera/audio, device proof, privacy/publishing, on-device compliance, transport/reliability, read-only debugging/observability, operational readiness/recovery, shared application architecture, reference implementation playbooks, source-aligned implementation recipes, Developer Center project/release operations, release evidence, and source refresh. The official source snapshot is DAT 0.9.0 for iOS/Android plus the current Web App repository; the user’s “Gen 3” wording remains `to-verify` until a public runtime mapping and physical-device result establish it.

## 2026-08-22 Meta Wearables extension

- Refreshed public Meta sources: the [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [Web Apps repository](https://github.com/facebook/meta-wearables-webapp), and [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/).
- Recorded the DAT 0.9.0 iOS/Android release anchors, iOS 17.2 minimum, current camera/session/Display migration boundaries, Web App 600×600/additive/input constraints, MockDevice/browser/physical evidence ladder, preview/publishing boundaries, and absence of a public Gen 3 runtime mapping in the Meta source registry.
- Added the initial nine-package [Meta Wearables extension team](../knowledge-base/skills/packages/README.md) with role-routing and evaluation fixtures. The later API-atlas tranche adds the tenth package. It intentionally distinguishes native DAT from Web Apps and does not claim physical glasses, authenticated Developer Center access, release-channel access, App Store approval, or production behavior.

## 2026-08-22 Meta DAT API/tooling atlas

- Added the [DAT iOS API surface atlas](../knowledge-base/70-meta-wearables/10-dat-ios-api-surface-atlas.md), [upstream skill/tooling map](../knowledge-base/70-meta-wearables/11-upstream-skill-and-tooling-map.md), and [API atlas role package](../knowledge-base/skills/packages/meta-dat-api-atlas/SKILL.md).
- Anchored the atlas to the public DAT iOS 0.9.0 commit, changelog, README, upstream skills, samples, public API reference, `llms.txt?full=true`, and Wearables MCP. It maps `MWDATCore`, `MWDATCamera`, `MWDATDisplay`, and `MWDATMockDevice` while labeling broader machine-index names and exact target symbols `to-verify` until the selected package compiles.
- Added the upstream conventions, sample-app, debugging, live-debugging MCP, Codex/plugin, and Web Apps boundary to the team routing. The public source still does not prove an account, release channel, App Store submission, Gen 3 mapping, or physical glasses behavior.

## 2026-08-22 Meta device and release evidence packet

- Added the [device and release evidence packet](../knowledge-base/70-meta-wearables/12-device-and-release-evidence-packet.md) with stable task IDs for source/static/build/mock/browser-simulator/connected/physical/signed/release-channel/production evidence.
- Defined run identity, observed fields, artifact naming, redaction rules, device-generation treatment, route-specific manual tasks for registration/session/camera/HFP/Display/Web Apps/recovery, and explicit stop conditions. It is a future execution contract; no physical or account-gated result is being claimed.

## 2026-08-22 Meta source-conflict refresh

- Rechecked the live DAT iOS/Android repositories, changelog, full Wearables
  reference, Web Apps toolkit, Web Apps agent/performance guidance, Developer
  Center entry points, and public MCP route. Recorded DAT iOS `main` versus the
  reproducible 0.9.0 tag and the Web Apps `main` commit in the [Meta source
  registry](../knowledge-base/sources/meta-wearables-source-registry.md).
- Captured the 0.9.0 migration deltas for camera ownership/stop, listener
  lifetime, Display capability/button groups, stream completion, doff errors,
  crash controls, MockDevice link checks, and target-sensitive background camera
  behavior.
- Reconciled an official Web Apps conflict: the full public index lists no text
  input/offline/back navigation while toolkit `main` documents a text composer,
  offline/service-worker, Escape/back, gesture, and sensor guidance. Those
  features now remain `source-conflict`/`to-verify` in the route, skills, and
  device-proof packet; no physical or account-gated result is claimed.

## 2026-08-22 Meta plugin matrix and Android parity

- Added the [public plugin and skill matrix](../knowledge-base/70-meta-wearables/13-public-plugin-and-skill-matrix.md) to map the ten upstream DAT iOS roles, ten DAT Android roles, and twelve Web Apps toolkit roles into the local specialist team.
- Added the [DAT Android parity and boundaries](../knowledge-base/70-meta-wearables/14-dat-android-parity-and-boundaries.md) route and the [DAT Android integration package](../knowledge-base/skills/packages/meta-dat-android-integration/SKILL.md), covering the 0.9 Maven artifacts, Kotlin lifecycle, `DatResult`, `Flow`/`StateFlow`, Manifest/privacy/R8 configuration, and Swift/Kotlin boundaries.
- Preserved separate source, build, MockDevice, connected-device, and physical evidence for Android; no Android target, account, physical glasses, Gen 3 mapping, or release result is claimed by this documentation expansion.

## 2026-08-22 Full-SDK capability audit

- Added the [full SDK capability and source-conflict matrix](../knowledge-base/70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md) covering the five iOS package products (four runtime products plus the test-only MockDevice client), four Android artifacts, Web Apps runtime, audio/sensor/update/debugging surfaces, privacy, and release evidence.
- Found and recorded actionable upstream drift: iOS guidance still contains an iOS 16 minimum and `DAMEnabled` example; Android guidance includes 0.8.0 examples, `DAM_ENABLED`, and `Session`/`DeviceSession` naming that conflicts with the 0.9.0 changelog.
- Added the [full-SDK audit package](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/SKILL.md), role routing, and evaluation fixture. It rejects unqualified “full SDK” claims and keeps phone microphone, HFP, mock, browser, connected, physical, signed, release-channel, and production evidence distinct.

## 2026-08-22 Device-generation and runtime-support refresh

- Added the [device-generation and runtime-support matrix](../knowledge-base/70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) and wired it into the route planner, full-SDK auditor, agentic team, device-proof route, evidence packet, fixtures, and source-refresh role.
- Rechecked official Meta product naming: Ray-Ban Meta Gen 2, Gen 2 Optics, and the separate Meta Glasses line are source-level product labels; DAT model-family identifiers and runtime capabilities remain separate evidence fields. The user’s “Gen 3” wording remains `to-verify`.
- The interactive [Developer Center](https://wearables.developer.meta.com/docs/develop/) surface was login-gated, while the raw [full-reference](https://wearables.developer.meta.com/llms.txt?full=true) and DAT-filtered endpoint returned readable public v0.9 source text. Authenticated compatibility/version-dependency and policy tables remain explicitly `access-gated`; the raw index is not a substitute for selected-package or physical-device proof.
- Added `GEN-SRC-01`, `GEN-STATIC-01`, `GEN-CONNECTED-01`, `GEN-PHYSICAL-01`, and `GEN-CROSS-01` to the evidence packet. No target build, account, connected-device, physical-glasses, release-channel, or production result is claimed.

## 2026-08-22 On-device compliance contract

- Added the [on-device compliance and runtime contract](../knowledge-base/70-meta-wearables/17-on-device-compliance-and-runtime-contract.md), separating `glasses-native`, `phone-local`, `remote`, `mixed`, and `unknown` processing from the marketing phrase “on-device.”
- Added the [on-device compliance specialist](../knowledge-base/skills/packages/meta-wearables-on-device-compliance/SKILL.md) and wired it into the Meta agentic team, full-SDK auditor, route planner, camera/audio, Display, Web Apps, privacy, device-proof, fixtures, and package indexes.
- Added `ODC-SOURCE-01`, `ODC-STATIC-01`, `ODC-MOCK-01`, `ODC-PHYS-01`, and `ODC-RELEASE-01` to the evidence packet. No implementation, remote-processing, account, physical-device, or release claim is being promoted by this documentation update.

## 2026-08-22 Full DAT reference journey inventory

- Expanded the [full-SDK capability matrix](../knowledge-base/70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md) with the DAT-filtered v0.9 reference sections for setup/hardware/version dependencies, iOS, Android, Display, lifecycle/permissions, HFP/A2DP, MockDevice, AI/MCP/tooling, organization/project/release-channel administration, and Web Apps.
- The inventory maps each section to a local route owner while keeping source lookup, package compilation, account access, connected-device behavior, physical glasses behavior, and production release as separate evidence levels.

## 2026-08-22 Security, attestation, and credential boundaries

- Rechecked the raw [full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true) and current [DAT iOS](https://github.com/facebook/meta-wearables-dat-ios) and [DAT Android](https://github.com/facebook/meta-wearables-dat-android) setup/permissions roles. The reference describes iOS `AppLinkURLScheme`, `MetaAppID`, `ClientToken`, and `TeamID`, Android `APPLICATION_ID`/`CLIENT_TOKEN`, Developer Mode versus release-channel attestation, and a dated DAT App Store warning tied to the current `ExternalAccessory`/MFi/privacy-manifest path.
- Added the [security, attestation, and credential-boundaries route](../knowledge-base/70-meta-wearables/25-security-attestation-and-credential-boundaries.md), the [security/attestation role](../knowledge-base/skills/packages/meta-wearables-security-attestation/SKILL.md), a redacted [contract reference](../knowledge-base/skills/packages/meta-wearables-security-attestation/references/security-attestation-contract.md), and `SEC-SOURCE-01` through `SEC-RELEASE-01` evidence rows.
- Wired the specialist through the Meta agentic team, route routing, evaluation fixtures, full-SDK matrix, Developer Center/privacy/on-device/operational roles, source registry/freshness log, package indexes, coverage, and GoalBuddy state. No credential, account, attestation, signed build, physical, App Store/Play, production, or Gen 3 claim is being made.

## 2026-08-22 Operational readiness and recovery

- Added the [operational readiness and recovery route](../knowledge-base/70-meta-wearables/18-operational-readiness-and-recovery.md) and [portable operational-readiness specialist](../knowledge-base/skills/packages/meta-wearables-operational-readiness/SKILL.md).
- The role freezes the mobile/DAT/companion/firmware/on-glasses-DAT-app/account/transport/channel tuple, separates Developer Mode from signed release-channel proof, classifies the first failing state, and records bounded recovery as attempted versus observed.
- Added `OPS-SOURCE-01`, `OPS-CONFIG-01`, `OPS-PAIR-01`, `OPS-RECOVERY-01`, `OPS-THERMAL-01`, and `OPS-CHANNEL-01` to the evidence packet. The raw full reference’s Display prerequisites, version-dependency access boundary, and first-party versus community troubleshooting signals remain explicitly separated; no physical or release result is claimed.

## 2026-08-22 Application architecture and platform boundaries

- Added the [application architecture and platform-boundaries route](../knowledge-base/70-meta-wearables/19-application-architecture-and-platform-boundaries.md) and [portable application-architecture specialist](../knowledge-base/skills/packages/meta-wearables-app-architecture/SKILL.md).
- The role defines shared product/domain state, iOS/Android/Web App adapters, native Display and phone fallback seams, session epochs, cancellation/resource ownership, bounded media queues, stale-event rejection, and layered reducer/fake/mock/browser/physical evidence.
- Added `ARCH-SOURCE-01`, `ARCH-STATIC-01`, `ARCH-TEST-01`, `ARCH-MOCK-01`, `ARCH-PHYS-01`, and `ARCH-RELEASE-01` to the evidence packet. Shared architecture and test seams remain implementation evidence, not proof of physical glasses parity or Gen 3 support.

## 2026-08-22 Android API surface atlas

- Added the [DAT Android API surface atlas](../knowledge-base/70-meta-wearables/20-dat-android-api-surface-atlas.md) and [portable Android API-atlas specialist](../knowledge-base/skills/packages/meta-dat-android-api-atlas/SKILL.md), creating an Android counterpart to the iOS API atlas.
- Mapped the four 0.9 Maven artifacts, `Wearables`/session/camera/Display/MockDevice/result/Flow lanes, Gradle/Manifest gates, Java interop, R8, audio/data boundaries, and source conflicts between upstream `Session` examples and the 0.9 `DeviceSession.addCamera(...)` changelog route.
- Added `AND-SOURCE-01`, `AND-CONFIG-01`, `AND-API-01`, `AND-MIGRATE-01`, `AND-MOCK-01`, `AND-BUILD-01`, `AND-PHYS-01`, and `AND-RELEASE-01` to the evidence packet. No Android target compile, account, physical glasses, Gen 3 mapping, or release result is claimed.

## 2026-08-22 Developer Center project and release operations

- Added the [Developer Center project and release operations route](../knowledge-base/70-meta-wearables/21-developer-center-project-and-release-operations.md) and [portable developer-operations specialist](../knowledge-base/skills/packages/meta-wearables-developer-operations/SKILL.md).
- Mapped Managed Meta Account organization/team membership, project and platform-app identity, product listing and permission rationale, version/build readiness, release channels and tester Meta Accounts, telemetry controls, and project recovery/destructive-operation boundaries.
- Added `DCO-SOURCE-01`, `DCO-ORG-01`, `DCO-PROJECT-01`, `DCO-VERSION-01`, `DCO-CHANNEL-01`, `DCO-TESTER-01`, `DCO-TELEMETRY-01`, and `DCO-RECOVERY-01` to the evidence packet. Public source guidance, authenticated Developer Center state, signed artifacts, and physical/release evidence remain separate; no account mutation or channel result is claimed.

## 2026-08-22 Transport, audio, and runtime reliability

- Added the [transport, audio, and runtime reliability route](../knowledge-base/70-meta-wearables/22-transport-audio-and-runtime-reliability.md) and [portable transport/reliability specialist](../knowledge-base/skills/packages/meta-wearables-transport-reliability/SKILL.md).
- Rechecked the live DAT iOS/Android 0.9 changelogs and setup routes. iOS explicitly adds Wi-Fi transport and local-network/Bonjour configuration for the relevant camera/display route; the reviewed Android 0.9 source establishes Bluetooth/Internet/session/camera/Display configuration but does not establish an equivalent DAT Wi-Fi contract.
- Added `TRN-SOURCE-01`, `TRN-CONFIG-01`, `TRN-LINK-01`, `TRN-AUDIO-01`, `TRN-STREAM-01`, `TRN-THERMAL-01`, `TRN-RECOVERY-01`, `TRN-PHYSICAL-01`, and `TRN-RELEASE-01` to the evidence packet. Transport, processing location, physical audio, thermal safety, and cross-platform parity remain separate evidence claims.

## 2026-08-22 Debugging, observability, and diagnostic evidence

- Re-read the official [DAT iOS debugging](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/debugging/SKILL.md), [iOS live-debugging MCP](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/live-debugging-mcp/SKILL.md), [DAT Android debugging](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/debugging/SKILL.md), and [Android live-debugging MCP](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/live-debugging-mcp/SKILL.md) roles at the current public repository revisions.
- Added the [debugging, observability, and diagnostic evidence route](../knowledge-base/70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) and [portable debugging/observability specialist](../knowledge-base/skills/packages/meta-wearables-debugging-observability/SKILL.md). It makes the read-only MCP baseline, first-failure graph, iOS/Android state map, bounded event wait, and redacted-bundle contract first-class team work.

## 2026-08-22 Input, sensors, and physical interaction

- Rechecked the public [full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true), the DAT iOS/Android Display skills, and the current [Web Apps agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md) and [Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md).
- Confirmed a useful boundary: native DAT Display exposes structured UI/action guidance, while the current public native repository snapshot does not establish a dedicated IMU/EMG/temple sensor module. The Web App toolkit describes D-pad/EMG focus input and browser motion/orientation/geolocation, but the full-reference index conflicts on several Web App features. Those features are now independently `source-conflict`/`to-verify`.
- Added the [input, sensors, and physical interaction route](../knowledge-base/70-meta-wearables/24-input-sensors-and-physical-interaction.md), [input/sensor specialist](../knowledge-base/skills/packages/meta-wearables-input-sensors/SKILL.md), normalized event/epoch contract, and `INP-SOURCE-01` through `INP-RELEASE-01` evidence rows. No native IMU symbol, physical gesture/sensor result, or Gen 3 mapping is claimed.
- Added `DBG-SOURCE-01`, `DBG-CONN-01`, `DBG-READINESS-01`, `DBG-BOUNDARY-01`, `DBG-PATH-01`, `DBG-EVENT-01`, `DBG-BUNDLE-01`, `DBG-REDACTION-01`, `DBG-PHYSICAL-01`, and `DBG-RELEASE-01` to the evidence packet. No live debug server, physical device, account mutation, or recovery result is claimed.

## 2026-08-22 Version dependency and device compatibility

- Rechecked the official [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), Android package registry, [full reference](https://wearables.developer.meta.com/llms.txt?full=true), and [version-dependencies page](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/). The public 0.9.0 release/artifact signals are available, while the exact dependency table is login-gated in this environment.
- Added the [version-dependency and device-compatibility evidence route](../knowledge-base/70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md), the [device-compatibility specialist](../knowledge-base/skills/packages/meta-wearables-device-compatibility/SKILL.md), a compact [compatibility contract](../knowledge-base/skills/packages/meta-wearables-device-compatibility/references/compatibility-contract.md), and `COMP-SOURCE-01` through `COMP-RELEASE-01` evidence rows.
- Recorded a closed public [Gen 2 firmware 126→127 report](https://github.com/facebook/meta-wearables-dat-ios/issues/265) only as a community troubleshooting signal. It does not establish official V127 support status. The new role requires exact phone/Meta AI/on-glasses DAT-app/firmware/artifact/runtime tuples and preserves “Gen 3” and “regular SDK” as unresolved until official and named-device evidence close them.
- Wired the role through the full-SDK matrix, agentic team, routing/fixtures, source registry/freshness log, package indexes, coverage, and GoalBuddy state. No compatibility table, target build, account, physical, release, or Gen 3 claim is being promoted.

## 2026-08-22 Source-pinned surface manifest

- Added the [source-pinned surface manifest route](../knowledge-base/70-meta-wearables/27-source-pinned-surface-manifest.md) and the portable [YAML manifest](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml) to make the five iOS package products (including the test-only MockDevice client), four Android artifacts, Web Apps journey, capability statuses, source conflicts, generation labels, evidence IDs, and refresh triggers consumable by agents.
- Updated the full-SDK auditor, agentic team, iOS/Android API-atlas roles, route indexes, and coverage references to load the manifest before making a “full SDK” or parity claim. The manifest remains a routing snapshot; generated API, authenticated Developer Center state, target builds, physical hardware, and release evidence remain separate.

## 2026-08-22 Version-pinned API surface register

- Added 30 normalized `api_surface.rows` to the portable manifest: iOS DAT core/registration/permissions/session/camera/media/audio/Display/health/mock/diagnostics, Android artifact/core/session/camera/Display/audio/mock/Java/health/diagnostics, Web Apps runtime/input/source conflicts/simulator/network/release proof, and the conceptual full-reference index lane.
- Each row carries official source anchors, evidence/status classification, compile or runtime gate, privacy path, typed fallback, and migration note. The API-atlas, Web Apps, full-SDK, and agentic-team roles now filter those rows before handing work to implementation specialists.
- The register is intentionally source-normalized rather than a generated API dump: exact SPM/Maven resolution, authenticated Developer Center values, target compilation, physical Display/audio/input behavior, release channels, and Gen 3 mapping remain open evidence gates.
- Added and ran the bundled [surface-manifest validator](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_surface_manifest.py), which checks schema/count drift, required API-row fields, source-anchor references, duplicate IDs, and credential-like content before packaging.

## 2026-08-22 Reference implementation playbooks

- Added the [reference implementation playbooks route](../knowledge-base/70-meta-wearables/28-reference-implementation-playbooks.md) and the portable [vertical-slice playbooks resource](../knowledge-base/skills/packages/meta-wearables-app-architecture/references/vertical-slice-playbooks.md).
- The five slices cover native Display glance cards, camera/photo to phone-local processing, audio-first/non-Display fallback, hosted Ray-Ban Display Web Apps, and a shared outcome across iOS/Android/native Display/Web Apps. Each carries manifest API rows, state/ownership rules, data-path and privacy boundaries, typed fallbacks, and source/build/mock/browser/connected/physical/release proof gates.

## 2026-08-22 Implementation recipes and build handoffs

- Added the [implementation recipes and build handoffs route](../knowledge-base/70-meta-wearables/29-implementation-recipes-and-build-handoffs.md), the portable [implementation-recipes skill](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/SKILL.md), and its [source-aligned recipe reference](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/references/implementation-recipes.md).
- The new specialist converts one selected playbook and manifest row set into iOS DAT, Android DAT, native Display, Web App, or shared-outcome scaffolding with explicit generated-API compile gates, ownership/epoch/stop order, bounded data paths, on-device/privacy classification, fallbacks, and evidence tasks. It does not claim that snippets compile or that a named Gen 2/Gen 3 pair supports the route.

## 2026-08-22 Target preflight and reproducible evidence

- Extended the [device-proof package](../knowledge-base/skills/packages/meta-wearables-device-proof/SKILL.md) with a portable [target-preflight reference](../knowledge-base/skills/packages/meta-wearables-device-proof/references/target-preflight.md) and validator.
- The preflight freezes iOS scheme/target and `Package.resolved`, Android module/variant and resolved Maven graph, or Web App revision/origin/input configuration, along with redacted identity, privacy/data-path, device-tuple, fallback, and next-gate fields. It uses `PRE-*` tasks before build, connected, physical, signed, or release claims; it does not promote a clean setup to hardware or production proof.
- Wired the playbooks into the application-architecture and Meta agentic-team packages. They make implementation handoffs repeatable without turning source rows, Gen 2/Gen 3 labels, MockDevice, or browser simulation into physical or production claims.

## 2026-08-22 Source revision drift checker

- Added the portable [public-ref checker](../knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_revisions.py) to the [source-refresh skill](../knowledge-base/skills/packages/meta-wearables-source-refresh/SKILL.md). It uses read-only `git ls-remote` calls to compare the pinned iOS `main`/`0.9.0` tag, Android `main`, and Web Apps `main` revisions without cloning repositories or handling credentials.
- Ran the checker against the current manifest: all four refs matched, with `CHECKS 4 DRIFT 0`. A future `DRIFT` is now an explicit refresh blocker requiring a receipt, source-conflict impact review, and package/archive refresh.

## 2026-08-22 Capability/evidence execution plan

- Added the portable [capability/evidence plan](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml) and [validator](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/scripts/validate_capability_evidence_plan.py). It maps all 14 manifest capabilities to owner roles, implementation route, privacy/data path, fallback, required evidence levels, preflight tasks, and proof task IDs.
- Wired the plan into the full-SDK auditor, agentic team, device-proof role, implementation-recipes role, source-manifest route, coverage matrix, and evaluation/routing handoffs. The validator enforces exact capability/surface/preflight alignment with the manifest, known task IDs, complete required evidence levels, and credential-free content.

## 2026-08-22 Upstream package/tree inventory

- Added `source_inventory` to the portable [surface manifest](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml) after checking the official iOS 0.9.0 `Package.swift`/tag tree, Android sample catalogs, and Web Apps toolkit tree. The inventory records five iOS products including the test-only `MWDATMockDeviceTestClient`, four Android 0.9.0 artifacts with sample SDK levels 31/36/36, and exact sorted role-name lists for ten iOS roles, ten Android roles, and twelve Web App roles, plus the reviewed sample/reference/template anchors.
- Added the verified iOS main-branch sample anchors: `CameraAccess` and `DisplayAccess`, plugin version 0.9.0, and DisplayAccess’s iOS 17.2+/Xcode 26.4+/Swift 6.3+ prerequisites. Clarified the runtime-versus-test-product boundary across the iOS foundations and atlas, full-SDK matrix, source-manifest route, full-SDK fixture, agentic routing, catalog, and coverage matrix.
- Added the machine-checked `terminology_contract` and incremented the manifest to `manifest_revision: 2` so “regular SDK” cannot silently become an invented third SDK family, “full SDK” routes to a composite audit, Ray-Ban Display resolves to native DAT Display or the separate Web Apps route, Gen 2 retains runtime gates, and Gen 3 remains unresolved. This is repository/package source evidence only; target compilation, authenticated Developer Center state, named-device behavior, physical glasses, and release proof remain open.
- Rechecked the live `llms.txt?full=true&product=dat` source and found the current official wording is `# DAT SDK v0.9` with explicit Gen 1/Gen 2, Optics, Display, and `MWDATCore` anchors; the earlier literal “WebApps SDK” wording was not present. Incremented the surface manifest to `manifest_revision: 3`, recorded those five terms, and extended the public-ref checker to `CHECKS 5 DRIFT 0`.
- Added and ran the portable [source-tree inventory checker](../knowledge-base/skills/packages/meta-wearables-source-refresh/scripts/check_source_tree_inventory.py). It performs 20 live checks against the pinned public Package.swift, plugin manifests and exact role directories, sample roots, Android artifacts/SDK tuple, Web Apps references/examples/templates, and current source revisions; the receipt is `CHECKS 20 DRIFT 0`.
- Extended the source inventory to include the three shared upstream root AI files (`AGENTS.md`, `README.md`, and `install-skills.sh`), each lane’s `.codex-plugin/plugin.json`, and the public docs MCP endpoint. Incremented the surface manifest to `manifest_revision: 4` and the team’s source-manifest pin to `4`; the refreshed checker receipt is `CHECKS 23 DRIFT 0`. These remain agent/source routing evidence only, not compile, account, device, physical, or release proof.

## 2026-08-22 Meta agent-team manifest

- Added the portable [Meta agent-team manifest](../knowledge-base/skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml) and validator after auditing the original goal against the existing role prose. It records the four delivery surfaces, exact 23 local specialist packages, all 32 upstream iOS/Android/Web Apps plugin-role handoffs, shared handoff fields, processing-location separation, and Ray-Ban Display/Gen 2/Gen 3 claim gates.
- Ran `validate_team_manifest.py` against the source-pinned surface manifest and all local role directories: `surfaces=4 local_roles=23 upstream_handoffs=32 device_claim_gates=3 evidence_levels=12`.
- Added the root AI-surface contract directly to the team manifest (`manifest_revision: 2`) and made its validator compare those paths with the source manifest inventory, so a portable team package retains the exact `AGENTS.md`/`README.md`/`install-skills.sh`, plugin-manifest, and docs-MCP routing inputs.
- Inspected the existing `bishoptech-sidequest` sibling as the first concrete target: its structural scan is `TARGETS_PRESENT` for iOS and Web App surfaces, its `Package.resolved` pins DAT iOS 0.9.0 at `9b1b83d791dfebff7afd452e924a256819094b64`, and its target wiring includes `MWDATCore`, `MWDATCamera`, and `MWDATDisplay`. Added a redacted implementation handoff and target-preflight receipt; no build, account, physical, signed, Gen 2, or Gen 3 claim was promoted.
- The target preflight found a stale/generated Xcode package checkout and then a startup volume with approximately 117–229 MiB free. The redundant generated cache backup created during diagnosis was removed; project sources and `Package.resolved` were not changed. A fresh source-tree live check also hit GitHub API HTTP 403 rate limiting, while the prior `CHECKS 23 DRIFT 0` receipt remains recorded.
- Re-ran the Tiny Detour target preflight sequentially after recovering disk space: `xcodebuild -list` and Debug `-showBuildSettings` passed, then `xcodebuild test` resolved DAT iOS `0.9.0` and passed `65` tests across `3` suites on the iOS `26.4` simulator. This is build/simulator evidence only; no connected, physical, account, signed, release, Gen 2, or Gen 3 claim was promoted.
- Added the portable device-proof `run_ios_target_preflight.py` runner and exercised both static and test modes against Tiny Detour. Its redacted receipt captures the Xcode project/scheme/target graph, safe Debug settings, privacy/entitlement paths, DAT `0.9.0` Package.resolved pin, and the same `65`-test/`3`-suite simulator result without printing raw xcodebuild output or credential values. The runner still marks connected, physical, generation, signed, and release claims as open.
- Re-ran the live Meta source-tree inventory after the earlier GitHub rate-limit response: all `23` checks returned `MATCH` with `DRIFT 0`. The live combined team preflight now passes target surface, team/surface/capability manifests, source tree, source revisions, and Tiny Detour's implementation handoff with decision `target-preflight`; it still stops before connected or physical proof.
- Added the Web Apps `run_webapp_preflight.py` receipt runner and ran it against Tiny Detour's local HTML board. Its referenced JavaScript passes Node syntax checking, but the source is correctly classified as `generic-web-surface` because `mrbd-web-app-capable=yes`, Meta description metadata, and hosted HTTPS delivery are absent; the required-Meta-marker run fails closed before browser-simulator or physical Display claims.
- Added the human-readable [agent-team roster and handoff contract](../knowledge-base/70-meta-wearables/30-agent-team-roster-and-handoff-contract.md) and wired the manifest into the agentic-team, full-SDK audit, and source-refresh packages. A role roster remains orchestration evidence; package compilation, account state, physical glasses, and release eligibility remain separate.

## 2026-08-22 Native DAT Display implementation slice

- Added the [source-aligned native iOS Display starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-display-starter/MetaWearablesDisplayStarter.swift) to the implementation-recipes package. It uses the DAT 0.9.0 iOS interfaces resolved from the selected target's XCFrameworks: `AutoDeviceSelector` with `supportsDisplay()`, `DeviceSession` state/error streams, `session.addDisplay()`, `Display.statePublisher`, `Display.send(FlexBox)`, structured `ButtonGroup` actions, and listener/display/session stop ordering.
- Type-checked the starter with Swift 6 against the actual `MWDATCore` and `MWDATDisplay` simulator frameworks at the target's iOS 26.0 deployment boundary: exit `0`, no diagnostics. The recipe-reference validator passed with `headings=11 markers=12 code_fences=8`; the package validator passed; and the rebuilt archive contains the starter without generated `.build`, `__pycache__`, or `.pyc` artifacts.
- This closes a reusable source/package compile gate only. It does not establish registration, account state, named Gen 2/Gen 3 compatibility, physical Display rendering, brightness/legibility, input timing, camera/audio behavior, signed artifacts, or release-channel proof.

## 2026-08-22 Native Android DAT Display implementation slice

- Re-read the official [Android DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess), its [DisplayViewModel source](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/DisplayAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/displayaccess/display/DisplayViewModel.kt), and the [Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md) at Android `main` revision `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc`.
- Added the [source-aligned Android Display starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-display-starter/MetaWearablesAndroidDisplayStarter.kt). It uses `SpecificDeviceSelector`, `DatResult.fold`, session `Flow` collectors, `addDisplay()`, `Display.state`, `sendContent`, `buttonGroup`, `removeDisplay()`, typed phone fallback, epoch checks, and child-before-parent teardown.
- The Android compile gate remains open: this knowledge-base workspace has no Android target, Android SDK build graph, or authenticated Maven artifact resolution. No Android compile, connected, physical, Gen 2/Gen 3, signed, or release claim is promoted by the source-aligned asset.

## 2026-08-22 Current DAT reference and Android naming recheck

- Re-fetched the [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat) and confirmed the public v0.9 hardware wording remains Ray-Ban Meta Gen 1/Gen 2, Ray-Ban Meta Optics, and Meta Ray-Ban Display glasses; no public Gen 3 runtime mapping was found. The compatibility routes retain “Gen 3” as `to-verify`.
- Re-read the official [Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md) and [DisplayAccess implementation](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/DisplayAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/displayaccess/display/DisplayViewModel.kt). The current sample uses `DeviceSession`; older upstream agent guidance still contains `Session` wording and 0.8-era examples. Updated the local Android parity, API atlas, integration fixture, and migration role to preserve the conflict while routing new 0.9 work through `DeviceSession` pending target compilation.
- Hardened the source-tree inventory checker with a codeload-archive fallback for GitHub Contents API rate limits. The live combined preflight then returned `TEAM_PREFLIGHT decision=target-preflight`, source-tree `CHECKS 23 DRIFT 0`, and source revisions `CHECKS 5 DRIFT 0` without credentials.

## 2026-08-22 Machine-checked compatibility evidence packet

- Added the [compatibility evidence-packet template](../knowledge-base/skills/packages/meta-wearables-device-compatibility/references/compatibility-evidence-packet.yaml) and [validator](../knowledge-base/skills/packages/meta-wearables-device-compatibility/scripts/validate_compatibility_packet.py). It requires the source snapshot, full product/runtime tuple, processing claim, capability fallbacks, all eight `COMP-*` evidence rows, open gates, next proof task, and redaction fields.
- The draft Gen 2 template validates successfully. The validator rejects sensitive values, unknown evidence IDs, incomplete tuples, and completed packets that lack connected tuple, physical capability, release, or Gen 3 evidence. This strengthens the handoff contract without claiming any new device or release support.

## 2026-08-22 Android DAT target bootstrap slice

- Re-read the official [Android `DisplayAccess` build graph](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess) and pinned the observed AGP `8.11.1`, Kotlin `2.2.21`, Gradle `8.14.1`, compile/target SDK `36`, min SDK `31`, Java/Kotlin JVM `17`, and DAT `0.9.0` artifact coordinates in a portable [Android target starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md).
- The starter is a target-owned permission/init shell around `Wearables.initialize(context)` with the official GitHub Packages repository and manifest metadata. `GITHUB_TOKEN`, Developer Center application/client values, and analytics/crash choices enter only through environment variables or ignored `local.properties`; no credential value is stored in the package.
- Wired the starter into the implementation-recipes skill, Android build handoff, project bootstrap packet, agent team, and completion audit. The Android compile gate remains open because this host has no Android SDK/Gradle executable or authenticated Maven path; no connected, physical, Gen 2/Gen 3, signed, or release claim is promoted.

## 2026-08-22 Native DAT camera implementation slice

- Re-read the official [iOS `CameraAccess` sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/CameraAccess), [Android `CameraAccess` sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/CameraAccess), and both 0.9.0 changelogs. The current contract is consolidated camera ownership: iOS `DeviceSession.addCamera(config:)` with `Camera.stream`, and Android `DeviceSession.addCamera(StreamConfiguration)` with `Camera.stream`; photo delivery remains a typed stream/result boundary rather than a shared raw-media queue.
- Added source-aligned [iOS](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift) and [Android](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt) camera/photo coordinators. Both keep raw frames inside the adapter, expose bounded first-frame/photo events, make permission and phone-local photo handoff explicit, and stop the camera child before the parent session.
- Type-checked the iOS coordinator on 2026-08-22 against the selected target's DAT 0.9.0 simulator `MWDATCore`/`MWDATCamera` XCFrameworks. The Android coordinator is aligned to the official `DatResult`/`Flow`/`CameraAccess` symbols but remains compile-open because this host has no Android SDK, Gradle executable, or authenticated Maven artifact cache.
- Wired the camera assets into the implementation-recipes, iOS integration, Android integration, camera/audio, API-atlas, implementation-handoff, and completion-audit routes. No camera, audio, physical glasses, named Gen 2/Gen 3, signed artifact, release-channel, or production claim is promoted by this slice.

## 2026-08-22 Android target-preflight runner

- Added the portable redacted [Android target-preflight runner](../knowledge-base/skills/packages/meta-wearables-device-proof/scripts/run_android_target_preflight.py), modeled on the existing iOS receipt runner. It inventories the Gradle root/module/variant, AGP/Kotlin/DAT versions, SDK levels, DAT coordinates, repository declaration, Manifest metadata/permissions, 0.9 migration markers, toolchain signals, and credential presence without printing credential values or resolving/publishing dependencies.
- Exercised it against the credential-safe Android target starter. It returned `status=pass`, `evidence_level=static`, `compileSdk=36`, `minSdk=31`, `targetSdk=36`, AGP `8.11.1`, Kotlin `2.2.21`, DAT `0.9.0`, all four public Android DAT artifacts, and the expected static target files; the dependency graph remains `not-run`.
- The current host still lacks Android SDK/Gradle/ADB/Kotlin tooling and authenticated Maven access, so this improves reproducibility without creating an Android compile, connected-device, physical, Gen 2/Gen 3, signed, or release claim.

## 2026-08-22 Native DAT MockDevice implementation slice

- Re-read the official iOS `mockdevice-testing` skill and the Android
  `CameraAccess` MockDevice fixture at the pinned public DAT 0.9.0 source set.
  The shared fixture contract is enable/configure → pair the explicit
  `.rayBanMeta`/`RAYBAN_META` model → power/fold/don/doff lifecycle → permission
  status/request outcomes → file or phone-camera feed/captured image →
  captouch → child-before-parent adapter teardown → unpair/disable.
- Added the [source-aligned iOS MockDevice starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift)
  and [Android MockDevice starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt).
  Both emit sanitized events only and keep raw URLs, media, identifiers, and
  credentials outside logs, shared state, fixtures, and archives.
- Type-checked the iOS starter with Swift 6 against the selected target's DAT
  0.9.0 simulator `MWDATCore`/`MWDATMockDevice` XCFrameworks: exit `0`,
  `IOS_MOCKDEVICE_TYPECHECK_OK`. The Android starter follows the official
  `MockDeviceKitInterface`, `MockGlasses`, `Permission`, `CameraFacing`, URI,
  and `DatResult.fold` shapes but remains compile-open because this host still
  has no Android SDK/Gradle executable or authenticated Maven artifact cache.
- Wired the fixtures into the implementation-recipes, iOS integration,
  Android integration, camera/audio, agent-team, build-handoff, and completion
  routes. Mock evidence remains deterministic logic/failure evidence only; it
  does not close radio, optics, HFP/A2DP, firmware, thermal, physical input,
  named Gen 2, unresolved Gen 3, signed, or release gates.

## 2026-08-22 Executable Meta Wearables team routing receipt

- Added the portable [capability/full-SDK routing receipt runner](../knowledge-base/skills/packages/meta-wearables-agentic-team/scripts/route_capability.py).
  It reads the machine-readable team manifest, source-pinned surface manifest,
  and capability/evidence plan without credentials or target mutation.
- `--full-sdk` exercised successfully and returned the composite route across
  all 14 capabilities, four delivery surfaces, 23 local roles, 32 upstream
  handoffs, the current preflight/evidence ladder, terminology guardrails, and
  the next vertical-slice action. `--capability native-display
  --surface native-dat-ios --json` also returned a focused iOS route with the
  exact owner/handoff/proof rows.
- The runner is deliberately evidence-conservative: it produces route/source
  evidence only and fails closed for unknown capability IDs, invalid surface
  filters, missing owner roles, or missing manifests. It does not claim package
  compilation, account access, registration, named-device capability, physical
  rendering, Gen 2 support, Gen 3 mapping, signing, or release.

## 2026-08-22 iOS MockDevice test-client implementation slice

- Inspected the selected DAT 0.9.0 `MWDATMockDeviceTestClient` simulator
  interface and official `CameraAccess` UI-test route. The test-only product
  exposes `MockDeviceTestClient(portFilePath:)`/`waitForServer`, explicit
  `pairDevice(deviceType: .rayBanMeta)`, lifecycle/captouch/media controls,
  sanitized device-state queries, health checking, and unpairing.
- Added the [source-aligned iOS MockDevice test-client starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift)
  with separate app-process/UI-test-process responsibilities, private device
  identifiers, sanitized count access, no raw media/logging, and deterministic
  teardown. It type-checks against the actual DAT 0.9.0 simulator
  `MWDATCore`/`MWDATMockDeviceTestClient` XCFramework interfaces:
  `IOS_MOCKDEVICE_TEST_CLIENT_TYPECHECK_OK`.
- Wired the test-only product into the implementation-recipes, iOS
  integration, device-proof, MockDevice evidence, completion-audit, and source
  log routes. This closes implementation guidance for the fifth iOS package
  product without claiming XCUITest execution, account access, physical
  glasses, Gen 2 capability, Gen 3 mapping, signing, or release behavior.

## 2026-08-22 Web App starter metadata and static preflight

- Re-ran the strict [Web App preflight runner](../knowledge-base/skills/packages/meta-wearables-web-apps/scripts/run_webapp_preflight.py)
  against the portable [Ray-Ban Display Web App starter](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-web-starter/).
  The first run failed closed because the starter had the MRBD marker and
  600×600 viewport but no `meta description`.
- Added the required description metadata, then re-ran with
  `--require-meta-markers --node-check`: `status=pass`, `evidence_level=static`,
  MRBD marker/viewport/description/local script/package checks passing, and the
  deterministic Node suite passing all five tests.
- This closes the portable Web App source/static gate only. The existing
  sibling’s generic local web surface is unchanged; public HTTPS delivery,
  browser-simulator behavior, Meta AI add/launch authorization, and physical
  Ray-Ban Display rendering/input remain separate gates.

## 2026-08-22 Unified static fixture-suite runner

- Added the portable [static fixture-suite runner](../knowledge-base/skills/packages/meta-wearables-agentic-team/scripts/run_static_fixture_suite.py)
  to give the team one machine-readable receipt across the dependency-free
  shared-domain tests, Web App Node/preflight checks, Android target preflight,
  surface/capability/team/recipe validators, and the composite full-SDK route.
- Exercised it with the selected DAT iOS simulator checkout. All 17 checks
  passed: the shared Swift domain suite ran 4 tests, the Web App suite ran 5
  tests and passed strict metadata/Node preflight, Android static preflight
  passed, all manifests/recipe validators and both target-intake handoffs
  passed, the full route receipt passed, and the four iOS
  camera/Display/MockDevice/test-client starters type-checked. The live source
  checks in the same run remain `CHECKS 23 DRIFT 0` and `CHECKS 5 DRIFT 0`.
- The suite preserves unavailable/not-run status and explicitly does not
  promote static/mock/typecheck results to account, connected, physical,
  Gen 2/Gen 3, signed, or release evidence.

## 2026-08-22 Cross-platform shared-glance implementation handoff

- Added the draft [shared-glance cross-platform handoff](../knowledge-base/70-meta-wearables/target-intakes/meta-wearables-shared-glance-cross-platform-handoff.yaml)
  for one outcome across iOS DAT Display, Android DAT Display, Ray-Ban Display
  Web Apps, shared typed state, and phone fallback. It carries the exact
  source-pinned iOS/Android/Web revisions, 21 API rows, 17 evidence tasks, 14
  owner roles, processing-location/retention/consent boundaries, epoch and
  teardown rules, and the named next proof task.
- The implementation-handoff validator passes the packet with
  `route=native-display api_rows=21 evidence_tasks=17 owner_roles=14`; the
  packet remains `draft` because no unified sibling target, authenticated
  project, connected device, physical Display, Gen 2, or Gen 3 runtime result
  exists yet.
- Linked the packet into the bootstrap, implementation-recipes, and completion
  audit routes so future work starts from one auditable first slice instead of
  flattening the native and Web App SDK surfaces.

## 2026-08-22 Official agent-surface contract refresh

- Re-read the current official [DAT iOS README](https://github.com/facebook/meta-wearables-dat-ios#readme), [DAT Android README](https://github.com/facebook/meta-wearables-dat-android#readme), and [Web Apps README](https://github.com/facebook/meta-wearables-webapp#readme). Meta now documents the agent-facing surfaces as first-class repository inputs: native DAT has local Codex plugin installs, Web Apps has the Meta Wearables marketplace route, and all three lanes expose root agent files plus the shared docs MCP.
- Added `agent_surface_contract` to the source-pinned manifest (`manifest_revision: 5`) and the team manifest (`manifest_revision: 3`). It records the exact native-DAT commands, Web Apps marketplace mode, source revisions, MCP endpoint/auth statement, `search_dat_docs` versus `search_webapps_docs`, and the local `callable=false` fallback.
- Extended the route receipt and validators so every full-SDK/capability handoff carries the official agent-surface contract. The team remains 23 local roles and 32 upstream plugin-role handoffs; this is a cross-cutting source/tooling contract, not an invented fourth SDK or a new runtime capability.
- This refresh is source/tool routing evidence only. It does not establish an Android build, a Meta account/channel, named Gen 2 or Meta Glasses/“Gen 3” support, physical Display/input/audio behavior, signing, or release eligibility.
- Rebuilt the affected `meta-wearables-agentic-team.skill` and
  `meta-wearables-full-sdk-audit.skill` archives. Final QA: unified fixture suite
  `status=pass` with 14 checks passed and one optional iOS checkout-dependent
  check `not-run`; live source checks `CHECKS 23 DRIFT 0` and
  `CHECKS 5 DRIFT 0`; Markdown `broken=0 fence_errors=0`; package/archive
  parity `42/42`; credential-like scan `0`.

## 2026-08-30 Web Apps repository relocation refresh

- Rechecked the official Web Apps repository with `git ls-remote --refs` and
  the public GitHub compare. The canonical repository is now
  `facebook/meta-wearables-webapp`; `main` is
  `a2714f862c61b1ce9c6cb624fc7e4938087102db`.
- The compare from the prior `facebookincubator` snapshot contains one commit
  and three changed files: `README.md`, `install-skills.sh`, and
  `.cursor-plugin/plugin.json`. It updates ownership/install metadata and the
  simulator name, with no API or runtime surface-row changes. The local
  Web Apps conflict rows therefore remain `source-conflict`/`to-verify`.
- Refreshed the canonical URLs, the source-pinned surface manifest to revision
  6, the team manifest to revision 4, and the cross-platform handoff’s Web Apps
  pin. The expected public-ref receipt is `CHECKS 5 DRIFT 0`; source/tree
  checks remain source evidence rather than build, account, device, physical,
  signing, or release proof.

## Refresh rule

When Apple documentation, SDK interfaces, availability, entitlements, privacy requirements, Human Interface Guidelines, hardware behavior, or release requirements change, use the [source refresh and availability package](../knowledge-base/skills/packages/ios-source-refresh-and-availability/SKILL.md). A refresh should identify the changed source signal, affected routes, current SDK facts, evidence level, uncertainty, and the next validation gate.

## Public boundary

This log records engineering research, not a claim of guaranteed Apple approval. Source reading, compilation, simulator behavior, physical-device behavior, signed artifacts, TestFlight, and production behavior remain separate evidence levels.
