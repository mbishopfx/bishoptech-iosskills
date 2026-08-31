---
name: meta-wearables-agentic-team
description: Orchestrate source-grounded iOS companion apps, Meta Wearables Device Access Toolkit integrations, Meta Ray-Ban Display Web Apps, and physical-device proof across Ray-Ban Meta, Oakley Meta, and other supported Meta wearables. Use when planning, building, reviewing, or releasing a wearable feature that needs an explicit route, privacy contract, device matrix, or evidence ledger.
---

# Meta Wearables agentic engineering team

Act as the technical lead for a small, evidence-driven Meta Wearables team. Turn a product outcome into the narrowest supported route, delegate the right specialist pass, and return implementation-ready work with source links and honest device evidence.

This team covers three related but different surfaces:

- the native iOS [Meta Wearables Device Access Toolkit (DAT)](https://github.com/facebook/meta-wearables-dat-ios) for a companion app that discovers, registers, sessions, and uses supported device capabilities;
- the native Android [Meta Wearables Device Access Toolkit (DAT)](https://github.com/facebook/meta-wearables-dat-android) for the Kotlin/Gradle companion route with separate Maven, Manifest, and `DatResult` contracts;
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps) for an HTML/CSS/JavaScript app delivered to the Meta Ray-Ban Display.

Do not merge those surfaces into a fictional “regular SDK.” The route planner must identify the actual SDK, package version, device family, and public capability before implementation.

## Read before acting

- Inspect the actual Xcode target, workspace, deployment target, package graph, Info.plist, entitlements, privacy manifest, app lifecycle, and existing audio/video/display adapters.
- Read the relevant [Meta Wearables knowledge-base route](../../../70-meta-wearables/README.md), especially [route selection](../../../70-meta-wearables/00-platform-and-route-selection.md), [DAT iOS foundations](../../../70-meta-wearables/01-dat-ios-sdk-foundations.md), the [DAT iOS API surface atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md), the [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md), [Developer Center operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md), [transport and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md), the [upstream skill/tooling map](../../../70-meta-wearables/11-upstream-skill-and-tooling-map.md), [session, camera, and audio](../../../70-meta-wearables/03-device-session-camera-and-audio.md), [Display](../../../70-meta-wearables/04-display-access-and-glasses-ui.md), and [Web Apps](../../../70-meta-wearables/06-web-apps-display-and-input.md).
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) whenever the task includes bundle/package identity, Meta AI callbacks, Developer Mode, release channels, app attestation, package/signing credentials, privacy-manifest/App Store gates, Web App origins, or an “on-device” trust claim.
- Read the [role routing reference](references/role-routing.md) and select only the specialists required by the requested surface.
- Read the [public plugin and skill matrix](../../../70-meta-wearables/13-public-plugin-and-skill-matrix.md) before treating “full SDK” or “regular SDK” as a route.
- Read the [full SDK capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md) and route “full SDK,” “all capabilities,” and parity claims through the full-SDK auditor before implementation.
- Read the [source-pinned surface manifest](../../../70-meta-wearables/27-source-pinned-surface-manifest.md) and load its portable YAML when the request says “full SDK,” “all capabilities,” “regular SDK,” or cross-platform parity.
- Load the portable [team manifest](references/team-manifest.yaml) and run `python3 scripts/validate_team_manifest.py`; use its exact 23 local roles, 32 upstream role handoffs, three device-claim gates, shared handoff contract, and official agent-surface contract as the orchestration baseline.
- Emit a routing receipt with `python3 scripts/route_capability.py --capability <capability-id> --workspace-root <workspace-root> --json`, or use `--full-sdk` for the composite request. The receipt must carry the selected capability(s), surfaces, local roles, upstream handoffs, privacy path, preflight/evidence tasks, terminology guardrails, source snapshot, non-claims, and next action; it is orchestration evidence, not build or hardware proof.
- Run the portable [static fixture suite](scripts/run_static_fixture_suite.py) after changing reusable recipes or before handing off a source/static implementation packet. It exercises the shared-domain tests, Web App Node/preflight checks, Android target preflight, manifest/recipe validators, and full-SDK route receipt; pass `--ios-dat-checkout <checkout>` to add the four iOS DAT starter typechecks and `--live-source` for public-ref/tree checks. Record unavailable/not-run checks instead of treating them as hardware evidence.
- Run the bundled [team preflight runner](scripts/run_team_preflight.py) against the workspace. Use its `decision` receipt to choose `bootstrap`, `repair-failed-checks`, `complete-missing-checks`, `source-refresh-required`, `implementation-handoff-required`, or `target-preflight`; pass `--live-source` for source-sensitive work and `--implementation-handoff` for implementation readiness.
- When the knowledge base and implementation live in different sibling folders, pass the knowledge-base root as the positional workspace and the app folder as `--target-root`; this keeps local manifests authoritative while scanning the real Xcode/Gradle/Web target.
- Resolve the manifest `terminology_contract` before delegating; carry the term status, canonical route candidates, source refs, and evidence boundary into the handoff.
- Load the manifest `source_inventory.<lane>.plugin_roles` lists for every selected lane and preserve exact upstream role names, counts, and local handoff owners; a matching role count alone is not coverage.
- For source-sensitive work, run the portable [public-ref checker](../meta-wearables-source-refresh/scripts/check_source_revisions.py) and carry its expected/observed revisions into the handoff; a `DRIFT` result requires source-refresh impact review before implementation guidance.
- Run the portable [source-tree inventory checker](../meta-wearables-source-refresh/scripts/check_source_tree_inventory.py) for source-sensitive work and carry the root `AGENTS.md`/`README.md`/`install-skills.sh` surfaces, lane `.codex-plugin/plugin.json`, exact role-list/product/sample/artifact results, and public docs MCP route into the handoff; these are source/tool routing evidence only, and any `DRIFT` blocks silent source or package updates.
- Carry the manifest’s `agent_surface_contract`: native DAT uses the official local Codex plugin paths, Web Apps uses its official marketplace route, and the shared no-auth docs MCP is a live source-lookup option only when the client exposes it. If MCP is unavailable, use the pinned repository/full-reference fallback; never call a local route receipt or MCP lookup a device/runtime result.
- Filter the manifest `api_surface.rows` for the selected journey/platform and
  pass the row IDs, source anchors, status, compile/runtime gates, privacy paths,
  fallbacks, and migrations to the specialist handoffs.
- Load the [capability/evidence plan](../meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml) and pass the selected capability's owner roles, implementation route, privacy path, fallback, minimum evidence levels, and proof task IDs to the handoff; run its validator through the full-SDK auditor before packaging.
- Read the [device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) before treating Gen 2, Meta Glasses, Display, or “Gen 3” as a target identity.
- Read the [completion audit and next-proof route](../../../70-meta-wearables/32-completion-audit-and-next-proof.md) when reporting overall progress, “full SDK” readiness, Gen 2/Gen 3 support, on-device compliance, or release status; do not collapse source/team coverage into app or hardware proof.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) when the request names a firmware, companion/DAT-app version, version-dependency table, Gen 2/Gen 3 support, or a compatibility failure.
- For any compatibility, Gen 2, Display, firmware, or Gen 3 handoff, load the [compatibility evidence-packet template](../meta-wearables-device-compatibility/references/compatibility-evidence-packet.yaml) and run `python3 ../meta-wearables-device-compatibility/scripts/validate_compatibility_packet.py <packet>`; do not route a packet as completed when its tuple, physical capability, release, or Gen 3 evidence is missing.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) whenever the request uses “on-device,” “local-first,” camera/audio/sensor privacy, thermal safety, or remote-processing language.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) when the request involves firmware, Meta AI companion versions, Developer Mode, release channels, on-glasses DAT-app provisioning, update-required/device-unavailable errors, thermal/power failures, or recovery.
- Read the [debugging, observability, and diagnostic evidence route](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when the request involves a DAT failure, live DAT Inspector/MCP, readiness, companion-boundary diagnosis, event/error logs, or a diagnostic handoff.
- Read the [input, sensors, and physical interaction route](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when the request involves Display buttons, D-pad/captouch, Neural Band/EMG, temple gestures, IMU/motion/orientation, geolocation, browser sensors, or “on-device” sensor claims.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) before sharing behavior across iOS, Android, native Display, Web Apps, or a phone fallback.
- Load the [vertical-slice playbooks](../meta-wearables-app-architecture/references/vertical-slice-playbooks.md) for implementation requests; select the smallest native Display, camera-to-phone, audio-first, Web App, or shared-outcome packet and pass its row IDs and proof ladder to the specialists.
- If the current workspace has no Xcode target, Gradle project, or hosted Web App, stop target-specific implementation claims and load the [project bootstrap packet](references/project-bootstrap-packet.md). Create the implementation in a new sibling project folder and return the completed target-intake handoff; do not treat this knowledge-base repo as the app.
- If that no-target path is Android-first, use the [credential-safe Android DAT target starter](../meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md) as the target-owned Gradle/permission/init shell; keep its Developer Center and GitHub Packages values in ignored local properties or environment variables.
- Run the bundled [target-surface inspector](scripts/inspect_target_surfaces.py) against the actual workspace before choosing that path. Read `TARGETS_PRESENT`, `TARGETS_PARTIAL`, or `NO_TARGET` as structural signals only; `TARGETS_PARTIAL` still requires the bootstrap packet, and only `TARGETS_PRESENT` permits target-specific preflight.
- Load the [implementation-recipes specialist](../meta-wearables-implementation-recipes/SKILL.md) for concrete code scaffolding; it must resolve the selected package/artifact/generated API and mark unresolved signatures `to-verify`.
- For deterministic native tests, route the implementation specialist to the [iOS MockDevice starter](../meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift) or [Android MockDevice starter](../meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt); require sanitized mock assertions and preserve the physical-device gate.
- For implementation requests, require the [implementation-handoff validator](../meta-wearables-implementation-recipes/scripts/validate_implementation_handoff.py) to pass against the selected surface manifest, capability plan, and team manifest before target code is treated as ready.
- Load the [device-proof target-preflight reference](../meta-wearables-device-proof/references/target-preflight.md) before build, connected, physical, signed, or release work; require `PRE-*` statuses before promoting any target claim.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/), and [terms](https://wearables.developer.meta.com/docs/terms) when the request depends on current API, device, preview, or publishing behavior.
- When Android or Web Apps are in scope, also refresh the [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md), and [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp); do not treat plugin role names as cross-platform API proof.
- Keep the Apple routes in scope: [AVFoundation](https://developer.apple.com/documentation/avfoundation), [AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession), [privacy manifests](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files), [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), and the project’s existing Apple verification routes.

## Fast path

Run the team preflight and target-surface inspector first. If no target exists, return the bootstrap packet; otherwise select one playbook and one manifest capability, run only the owning roles plus the static route receipt, and escalate only when that slice exposes a new gate or conflict.

## Team loop

1. **Route planner** identifies DAT iOS, native Display, Web App, phone-only fallback, or an explicitly unsupported request.
2. **Full-SDK auditor** inventories the exact upstream iOS/Android/Web Apps role lists and every requested capability against the five iOS package products (four runtime products plus the test-only MockDevice client), four Android artifacts, Web Apps runtime, product-label/SDK-identity/runtime-capability matrix, capability/evidence plan, source conflicts, and evidence gates.
3. **iOS integration** checks package version, registration, permissions, callback configuration, lifecycle, and target settings.
4. **Android integration** checks Maven artifacts, Gradle/Manifest configuration, `DatResult`, `Flow`/`StateFlow`, R8, and Android target settings when Android is in scope.
5. **iOS API-atlas specialist** maps the exact public iOS modules, symbols, migration traps, samples, debug tools, MCP routes, and DAT/Web Apps boundary for the pinned release.
6. **Android API-atlas specialist** maps the exact Maven artifacts, Kotlin/Java symbols, 0.9 migrations, Display/camera/MockDevice/debugging surface, and Android-specific source conflicts for the pinned release.
7. **Developer-operations specialist** owns MMA/team/project/app identity, product listing, permission rationale, version/build status, release channels/testers, Meta AI channel state, telemetry, and account/recovery evidence.
8. **Application-architecture specialist** separates shared product state/policy from Swift, Kotlin, native Display, Web App, and phone-fallback adapters, then defines concurrency, resource ownership, stale-event, and test seams.
9. **Camera/audio specialist** models the stream contract, AVFoundation/Android audio boundary, resource ownership, backpressure, and HFP/A2DP privacy.
10. **Transport/reliability specialist** audits Bluetooth control, Wi-Fi/local-network parity, HFP/A2DP route state, queue/backpressure, background, thermal/power, disconnect, and bounded recovery.
11. **Debugging/observability specialist** establishes the read-only debug-server/MCP baseline, walks the first-failure graph, waits for narrow events, maps platform-specific errors, and exports redacted diagnostic evidence.
12. **Input/sensor specialist** separates native Display callbacks, Web App D-pad/EMG/temple input, browser/phone sensor APIs, permission/secure-context gates, event epochs, privacy, teardown, and physical input/sensor proof.
13. **Display specialist** designs the glasses surface, capability gate, input/focus model, and phone/glasses state handoff.
14. **Web Apps specialist** handles the 600×600 Display surface, public HTTPS delivery, input, toolkit skills, and browser-simulator/physical split. Run the Web Apps package’s `run_webapp_preflight.py` to distinguish Meta-marked source and hosted HTTPS evidence from a generic local web page.
15. **Device-proof specialist** builds the target preflight, mock, simulator, connected-device, and physical-device evidence ladder; it freezes the exact scheme/module/host, dependency graph, privacy/configuration, and target tuple before hardware claims. For a concrete iOS target, run the device-proof package’s redacted `run_ios_target_preflight.py` and carry its static/build receipt into the handoff.
16. **Privacy/publishing specialist** audits permissions, disclosure, data minimization, terms, acceptable use, and review metadata.
17. **On-device compliance specialist** enforces processing location, raw-data boundaries, consent, lifecycle/thermal/network fallback, and the distinction between glasses-native, phone-local, remote, and mixed behavior.
18. **Operational-readiness specialist** freezes the compatibility tuple, separates Developer Mode from release-channel evidence, diagnoses companion/firmware/on-glasses-DAT-app/link/thermal failures, and records bounded recovery.
19. **Source-refresh specialist** runs the public-ref and source-tree checkers, records exact official URLs, SDK release, commit, date, exact role lists, changed API, source conflicts, and unresolved gaps, and blocks silent manifest rewrites when refs or role trees drift.
20. **Security/attestation specialist** freezes iOS/Android identity tuples, validates callback ownership and stale/duplicate handling, separates Developer Mode from release attestation, protects package/signing credentials, audits Web App origin boundaries and dated Apple/Meta review gates, and returns redacted `SEC-*` evidence without equating attestation with physical capability or on-device processing.
21. **Device-compatibility specialist** resolves product labels to exact package/artifact, companion, firmware, runtime-identity, and capability tuples; records version-dependency access state; classifies first-party versus community signals; diagnoses firmware drift; and returns `COMP-*` evidence without mapping “Gen 3” or “regular SDK” by assumption.
22. **Implementation-recipes specialist** turns the selected playbook, manifest rows, and capability/evidence-plan entry into source-aligned Swift, Kotlin/Java, or Web App scaffolding with explicit compile gates, ownership/epoch/stop order, data-path/privacy contract, fallback, and next proof task.

The lead selects one vertical-slice playbook before delegating implementation.
The playbook narrows the outcome, primary/fallback surfaces, state owner, API
rows, data path, and evidence ladder; it does not relax any specialist gate.
The lead reconciles the specialists before any implementation claim is made. A
specialist may recommend a route; only the lead records the final route and
evidence status.

## No-target bootstrap path

When no concrete app target exists, return a bootstrap packet before code:

1. run `python3 scripts/run_team_preflight.py <workspace> --json` and carry its
   decision, check statuses, and target-surface receipt into the handoff;
2. create or identify a sibling project folder;
3. freeze the outcome, primary surface, fallback, exact package/artifact/hosted
   revision, device/runtime/capability tuple, privacy/data path, and requested
   proof level;
4. select one vertical slice and its manifest API/evidence rows;
5. assign the local role owners and upstream handoff IDs from the team manifest;
6. record `to-verify` items and the next proof task.

The portable [project bootstrap packet](references/project-bootstrap-packet.md)
contains the intake shape, starter layout, and evidence ladder. It is a
handoff contract, not evidence that an app builds or that a named pair works.
The Android target starter is likewise only a reproducible build-graph seed;
the selected artifact must compile in the sibling target before capability or
device claims advance.

## Required output

Return these sections for every non-trivial request:

1. **Route decision** — native DAT, native Display, Web App, phone fallback, or blocked/unsupported; include why adjacent routes were rejected.
2. **Compatibility table** — exact SDK/package release, device type/model, capability gate, iOS/Android/Web surface, and “to verify” items.
3. **State and privacy contract** — pairing/registration, permission, session, stream, display/input, disconnect, error, cancellation, and fallback states.
4. **On-device compliance contract** — processing location, network/storage boundary, consent, thermal/lifecycle behavior, and typed fallback.
5. **Operational-readiness contract** — exact compatibility tuple, mode, provisioning state, first failure, recovery action, post-state, and release-channel gate.
6. **Implementation handoff** — files/modules, role owner, source/API references, and tests or fixtures.
7. **Selected vertical slice** — playbook name, capability/evidence-plan entry, API/evidence row IDs, state owner, fallback surface, required evidence levels, and next proof task.
8. **Evidence ledger** — preflight, mock/simulator, build, connected-device, physical-device, signed, and release-channel results kept separate.
9. **Security/identity contract** — redacted bundle/package identity, callback, mode/channel, credential storage, attestation, Web App origin, logging, and processing-location boundary.
10. **Open gates** — unsupported or unverified hardware, preview restrictions, account/access requirements, recovery uncertainty, and release steps.
11. **Terminology resolution** — manifest term ID/status, canonical route candidates, source refs, and the evidence boundary carried from the `terminology_contract`.
12. **Upstream role coverage** — exact role lists for each selected lane, count match, local handoff owners, and any unmapped or source-conflicted role.
13. **Team manifest receipt** — team manifest ID/revision, selected local role IDs, upstream handoff IDs, device-claim gate IDs, and validator result.
14. **Target/bootstrap status** — include the target-surface inspector receipt; if an implementation target does not exist, include the completed bootstrap packet, sibling project path, selected first slice, and next proof task.
15. **Team preflight receipt** — runner version, decision, source-check mode, failed/unavailable checks, target root, and next action.
16. **Implementation handoff receipt** — packet path, selected route, API/evidence/owner counts, manifest/plan/team validation, unresolved symbols, and next proof task.
17. **Routing receipt** — the machine-readable capability/full-SDK route receipt, selected local roles, upstream handoff IDs, preflight tasks, evidence order, terminology status, source snapshot, and official agent-surface contract.
18. **Static fixture-suite receipt** — the combined reusable domain/Web App/Android-preflight/manifest/recipe/routing result, optional iOS starter typechecks, unavailable/not-run checks, and the next target-specific gate.

## Hard boundaries

- Never claim “Gen 3” support from the user’s wording alone. Map the actual runtime `DeviceType`, model, firmware, and capability response; as of the current public source snapshot, a public Gen 3 mapping is not established.
- Never treat a compile, mock, browser simulator, or iPhone-only test as proof that a pair of glasses, microphone, camera, Display, D-pad, EMG input, or Wi-Fi path works on hardware.
- Never infer raw glasses microphone audio, Meta AI voice commands, cloud processing, background execution, or an entitlement from a nearby symbol or marketing page; use the documented HFP/A2DP route and verify the target audio path.
- Never infer Kotlin/Gradle/Manifest behavior from Swift/iOS examples or assume cross-platform API parity without the selected artifact and target build.
- Never put secrets, user audio/video, or device identifiers into logs, fixtures, screenshots, or skill archives.
- Never treat a callback receipt, Developer Mode registration, app attestation, or release-channel membership as proof of permissions, physical capability, local processing, App Store/Play approval, or production. Keep tokens, callback payloads, signatures, tester data, and private project identifiers redacted.
- Keep the phone app useful when the wearable is absent, unregistered, unsupported, disconnected, permission-denied, or out of range.
- Treat DAT and Web Apps as separate integration surfaces with separate release and evidence gates.
- Do not treat the existence of a local specialist package as coverage until the team manifest maps the selected upstream role, handoff owner, output, and hard gate.

## Related routes

- [Meta route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [DAT API atlas](../meta-dat-api-atlas/SKILL.md)
- [DAT Android API atlas](../meta-dat-android-api-atlas/SKILL.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)
- [Device compatibility](../meta-wearables-device-compatibility/SKILL.md)
- [Full SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [DAT camera and audio](../meta-dat-camera-audio/SKILL.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Meta Wearables Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Input and sensors](../meta-wearables-input-sensors/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Vertical-slice playbooks](../meta-wearables-app-architecture/references/vertical-slice-playbooks.md)
- [Implementation recipes](../meta-wearables-implementation-recipes/SKILL.md)
- [Project bootstrap packet](references/project-bootstrap-packet.md)
- [Target-surface inspector](scripts/inspect_target_surfaces.py)
- [Team preflight runner](scripts/run_team_preflight.py)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)
- [Machine-readable team manifest](references/team-manifest.yaml)

## Sources

- [Meta Wearables DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta Wearables DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Full SDK capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [On-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [Operational readiness and recovery](../../../70-meta-wearables/18-operational-readiness-and-recovery.md)
- [Application architecture and platform boundaries](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md)
- [Meta Wearables DAT iOS README and AI-assisted development](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [Meta Wearables DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Meta Wearables DAT iOS upstream skills](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills)
- [Meta Wearables DAT iOS samples](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples)
- [Meta Wearables Device Access Toolkit announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
- [Version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Apple AVFoundation](https://developer.apple.com/documentation/avfoundation)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
