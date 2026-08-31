# Meta Wearables knowledge base

This lane is the source-and-evidence layer for building native iOS/Android apps
and Meta Ray-Ban Display Web Apps that use Meta Wearables. It is deliberately
separate from the Apple framework routes because the wearable path crosses an
iPhone process, the Meta AI companion app, device firmware, a transport link,
and (for Web Apps) a hosted HTML/CSS/JavaScript surface.

## Current source snapshot

The pages in this tranche were refreshed on 2026-08-22 against the public
official repositories and documentation surfaces. The DAT repositories both
identify release 0.9.0 on 2026-08-03; pin the exact package revision in a real
app instead of treating this date as a permanent latest-version claim.

| Route | What it owns | Current evidence boundary |
| --- | --- | --- |
| Native DAT iOS | iOS integration, registration, device sessions, camera/stream/photo, and Display capability | Source/SDK route only until the target app, Meta AI account, glasses, firmware, and release channel are tested. |
| Native DAT Android | Android parity, Kotlin/Gradle/Manifest integration, and cross-platform naming/configuration comparisons | Reference route; use the Android package and selected Maven artifact for Android implementation. |
| DAT Android API atlas | Exact Android Maven artifacts, Kotlin/Java symbols, 0.9 migrations, Display/camera/MockDevice/debugging boundaries, and Android compile gates | Source/API atlas; the selected artifact and target build remain authoritative. |
| DAT Display | Structured visual content and video on display-capable glasses | Display capability must be selected and observed at runtime; it is not a property to infer from a frame name. |
| Web Apps | HTML/CSS/JavaScript rendered on Meta Ray-Ban Display | Browser simulator and hosted URL are development evidence; physical display and release-channel behavior remain separate. |
| Phone/system fallback | SwiftUI, AVFoundation/AVAudioSession, local persistence, and a graceful audio-first or phone-first experience | Apple source/target/device evidence is required independently of Meta hardware evidence. |
| Operational readiness | Companion, firmware, on-glasses DAT-app, transport, thermal/power, Developer Mode, release channels, and recovery | Compatibility tuple and physical/system result are required; source/issues alone do not prove provisioning or recovery. |
| Application architecture | Shared product state/policy, platform adapters, native Display/Web App presenters, phone fallback, concurrency, and test seams | Shared architecture does not prove platform parity, package symbols, or physical hardware behavior. |
| Reference implementation playbooks | Native Display, camera-to-phone-local, audio-first, Web App, and shared-outcome vertical slices with API/evidence row IDs and fallback contracts | Playbooks make implementation handoffs repeatable; exact package/API, target build, physical, and release proof remain separate. |
| Implementation recipes and build handoffs | Source-aligned Swift, Kotlin/Java, and Web App skeletons for selected API rows and playbooks | Recipes accelerate implementation but keep generated signatures, target configuration, physical behavior, and release proof compile- or device-gated. |
| Developer Center operations | Managed Meta Account organization/team membership, project/app identity, product listing, permission rationale, version/build state, release channels, testers, telemetry, and recovery | Public flow is source evidence; authenticated organization/project/channel state and destructive operations remain access-gated and require explicit authorization. |
| Transport and runtime reliability | Bluetooth control, Wi-Fi/local-network parity, HFP/A2DP, bounded camera/Display streams, route changes, thermal/power, disconnect, and recovery | Declared permissions or a connected link do not prove negotiated transport, physical audio, sustained streaming, processing location, or cross-platform parity. |
| Debugging and observability | Read-only DAT Inspector/live-debugging MCP, first-failure diagnosis, platform-specific state/error maps, redacted diagnostic bundles, and evidence-plane separation | App-visible debug events do not prove companion internals, physical behavior, release eligibility, or a successful recovery mutation. |
| Input, sensors, and physical interaction | Native Display callbacks, Web App D-pad/EMG/focus guidance, motion/orientation/geolocation source conflicts, normalized event epochs, sensor privacy, and named-target proof | Full-reference IMU wording, Web App toolkit sensor/input guidance, browser APIs, and physical gesture/sensor behavior remain separate claims. |
| Security, attestation, and credential boundaries | iOS/Android identity tuples, Meta AI callback validation, Developer Mode versus attested release channels, package/signing secrets, privacy-manifest/App Store gates, redaction, and security evidence | Source/configuration does not prove account access, attestation, signing, physical capability, local processing, or App Store/Play/production eligibility. |
| Version dependency and device compatibility | Versioned DAT iOS/Android migrations, Android artifact availability, authenticated version-table access state, firmware drift, product-label/runtime separation, Gen 2 evidence, and Gen 3/“regular SDK” routing | Public 0.9.0 source and a community issue do not establish current firmware support, a Gen 3 mapping, or universal capability behavior. |
| Source-pinned surface manifest | Machine-readable journey, module/artifact, terminology, capability, conflict, generation, refresh, and capability/evidence-plan inventory for full-SDK routing | Manifest and plan are routing contracts; exact package/API, account, target, physical, and release evidence remain authoritative. |
| Agent team roster and handoff contract | Machine-checked 23-role local roster, 32 upstream plugin-role handoffs, shared evidence contract, claim gates, and a consolidated team-preflight receipt | Team ownership and preflight checks are orchestration evidence; they do not prove a target build, account state, physical behavior, or release. |
| Project bootstrap and target intake | A sibling-project handoff for requests that arrive before an Xcode target, Gradle project, or hosted Web App exists | The packet freezes route, target tuple, first vertical slice, fallback, privacy path, and proof task; it does not build the app or prove hardware. |
| Existing target intake and preflight | Redacted target-routing receipt for the existing Tiny Detour iOS/Web sibling, its DAT 0.9.0 lockfile/products, privacy boundary, and current preflight gaps | Target structure and lockfile are static evidence; disk/API-rate-limit failures, build, account, physical, signed, and release gates remain separate. |
| Completion audit and next proof | Requirement-by-requirement status for KB coverage, full DAT routes, Display/Gen 2/Gen 3 claims, on-device contracts, app targets, and release evidence | This page is a status contract; only authoritative target, account, physical, signed, and release artifacts can close its open rows. |

Meta's public materials present native DAT and Display Web Apps as distinct
development paths. When a request says “regular SDK,” this knowledge base
routes it to the native DAT path or the Web Apps path only after the desired
surface is identified; it does not invent a third SDK.

## Read in this order

1. [Platform and route selection](00-platform-and-route-selection.md)
2. [DAT iOS foundations](01-dat-ios-sdk-foundations.md)
3. [Registration, permissions, and configuration](02-registration-permissions-and-configuration.md)
4. [Device sessions, camera, and audio boundaries](03-device-session-camera-and-audio.md)
5. [Display Access](04-display-access-and-glasses-ui.md)
6. [Device models and capability matrix](05-device-models-and-capability-matrix.md)
7. [Web Apps display and input](06-web-apps-display-and-input.md)
8. [MockDevice testing and evidence](07-mockdevice-testing-and-evidence.md)
9. [Privacy, publishing, and release](08-privacy-publishing-and-release.md)
10. [Source refresh and version history](09-source-refresh-and-version-history.md)
11. [DAT iOS API surface atlas](10-dat-ios-api-surface-atlas.md)
12. [Upstream DAT skills and tooling map](11-upstream-skill-and-tooling-map.md)
13. [Device and release evidence packet](12-device-and-release-evidence-packet.md)
14. [Public plugin and skill matrix](13-public-plugin-and-skill-matrix.md)
15. [DAT Android parity and boundaries](14-dat-android-parity-and-boundaries.md)
16. [Full SDK capability and source-conflict matrix](15-full-sdk-capability-and-source-conflict-matrix.md)
17. [Device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
18. [On-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
19. [Operational readiness and recovery](18-operational-readiness-and-recovery.md)
20. [Application architecture and platform boundaries](19-application-architecture-and-platform-boundaries.md)
21. [Reference implementation playbooks](28-reference-implementation-playbooks.md)
22. [Implementation recipes and build handoffs](29-implementation-recipes-and-build-handoffs.md)
23. [DAT Android API surface atlas](20-dat-android-api-surface-atlas.md)
24. [Developer Center project and release operations](21-developer-center-project-and-release-operations.md)
25. [Transport, audio, and runtime reliability](22-transport-audio-and-runtime-reliability.md)
26. [Debugging, observability, and diagnostic evidence](23-debugging-observability-and-diagnostic-evidence.md)
27. [Input, sensors, and physical interaction](24-input-sensors-and-physical-interaction.md)
28. [Security, attestation, and credential boundaries](25-security-attestation-and-credential-boundaries.md)
29. [Version-dependency and device-compatibility evidence](26-version-dependency-and-device-compatibility-evidence.md)
30. [Source-pinned surface manifest](27-source-pinned-surface-manifest.md)
31. [Agent team roster and handoff contract](30-agent-team-roster-and-handoff-contract.md)
32. [Project bootstrap and target intake](31-project-bootstrap-and-target-intake.md)
33. [Existing target intake and preflight](33-existing-target-intake-and-preflight.md)
34. [Completion audit and next proof](32-completion-audit-and-next-proof.md)

The reusable specialist packages live under
[the Meta Wearables skill team](../skills/packages/README.md). The central
Apple evidence vocabulary remains the contract for both lanes:
[evidence and verification language](../00-foundations/05-evidence-and-verification-language.md).

## Non-negotiable boundaries

- The Meta AI companion app, wearable firmware, DAT app on the glasses, iOS
  target configuration, device capability, and release channel are separate
  gates. Registration success does not prove a camera or Display session.
- `MockDeviceKit`, a browser simulator, a compile, or a source reading is not
  physical glasses proof. Name the exact device, OS, firmware, app build, and
  task for physical/system evidence.
- Use runtime device metadata and capability predicates such as
  `supportsDisplay()` rather than hard-coding a consumer generation label. The
  current public SDK model names include `rayBanMeta`, `rayBanMetaOptics`, and
  `metaGlasses`; this snapshot found no official source mapping “Gen 3” to one
  of them.
- Camera images, HFP audio, transcripts, display content, device identifiers, and
  external API results need a retention, disclosure, deletion, and logging
  policy. Model output is a proposal, not device or domain truth.
- Attestation, Developer Mode, release-channel identity, callback receipt, and
  “on-device” processing are separate claims. Keep all tokens, callback
  payloads, signatures, tester data, and private project identifiers redacted.
- A consumer label, model enum, SDK version, or registration success does not
  prove a capability on every firmware. Record the exact phone, Meta AI,
  on-glasses DAT-app, firmware, artifact, runtime identity, and evidence level;
  keep “Gen 3” `to-verify` until official mapping and named-device evidence
  exist.
- DAT is a developer-preview surface in the current public materials. Do not
  promise public publishing eligibility, Meta approval, App Store approval, or
  production behavior from documentation alone.

## Sources

- [Meta Wearables Device Access Toolkit announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Official DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Official DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Official Meta Wearables Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Meta Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Apple privacy manifest documentation](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Evidence and verification language](../00-foundations/05-evidence-and-verification-language.md)
