---
name: meta-wearables-source-refresh
description: Refresh the Meta Wearables DAT, Web Apps, device, terms, and Apple integration knowledge base with exact official URLs, release/tag/commit, retrieval date, API migrations, access gaps, and evidence boundaries, including a portable public Git ref drift check. Use before version-sensitive implementation, after an SDK release, or when a device-generation claim may have drifted.
---

# Meta Wearables source refresh

Keep the knowledge base current without turning an inaccessible page, remembered API, or product announcement into an implementation fact.

## Read before acting

- Read [Meta source freshness](../../../sources/meta-wearables-source-freshness-log.md), [Meta source registry](../../../sources/meta-wearables-source-registry.md), and the Apple team’s [source provenance rules](../ios-source-refresh-and-availability/references/provenance-and-evidence.md).
- Inspect the current local package manifests, lockfiles, sample code, generated API docs, and existing source notes.
- Run `python3 scripts/check_source_revisions.py` from this package before interpreting the pinned iOS/Android/Web App refs as current; it checks public `main` refs and an exact iOS reproducible tag without cloning or printing credentials.
- Run `python3 scripts/check_source_tree_inventory.py` after the ref check; it reads the pinned public root `AGENTS.md`/`README.md`/`install-skills.sh` surfaces, lane `.codex-plugin/plugin.json` manifests, Package.swift, exact role names, sample catalogs, artifact catalogs, SDK levels, Web App references, examples, and templates, then fails on inventory drift without cloning or handling credentials. It prefers the public Contents API and falls back to a read-only codeload archive on unauthenticated rate limits. A clean current receipt is `CHECKS 23 DRIFT 0`.
- Run `python3 ../meta-wearables-agentic-team/scripts/validate_team_manifest.py` after role-tree changes; it verifies the 23 local role packages, all 32 upstream role handoffs, and the Ray-Ban Display/Gen 2/Gen 3 claim gates.
- Read the [full SDK capability and source-conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md) before declaring module or capability coverage complete.
- Read the [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md) when refreshing Android artifacts, symbols, or 0.9 migration notes.
- Read the [device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md) before resolving product labels, “Gen 3,” or model-enum claims.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) when refreshing firmware, companion/DAT-app, artifact, version-table, or compatibility claims.
- Read the [on-device compliance and runtime contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) before updating processing-location, privacy, thermal, network, retention, or fallback claims.
- Read the [operational readiness and recovery route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md) before updating firmware, companion, on-glasses DAT-app, version-dependency, Developer Mode, release-channel, known-issue, or recovery claims.
- Read the [application architecture and platform-boundaries route](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md) before changing shared state, adapter, concurrency, lifecycle, or cross-platform parity guidance.
- Read [Developer Center project and release operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md) when the raw reference changes organization, project, version, channel, tester, telemetry, or recovery guidance.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when a source changes identity keys, callback/attestation semantics, package credentials, App Store/privacy-manifest requirements, Web App origin rules, or “on-device” claim boundaries.
- Read [transport, audio, and runtime reliability](../../../70-meta-wearables/22-transport-audio-and-runtime-reliability.md) when a changelog, setup guide, artifact, audio route, local-network requirement, transport parity signal, thermal behavior, or recovery claim changes.
- Read [debugging, observability, and diagnostic evidence](../../../70-meta-wearables/23-debugging-observability-and-diagnostic-evidence.md) when upstream debugging roles, live MCP tools, event schemas, known issues, or diagnostic-bundle behavior changes.
- Read [input, sensors, and physical interaction](../../../70-meta-wearables/24-input-sensors-and-physical-interaction.md) when a Display/input/sensor source, browser API, physical interaction, processing-location, or device-generation claim changes.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios), [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android), [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md), [full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true), [Web Apps repository](https://github.com/facebook/meta-wearables-webapp), [Developer Center](https://wearables.developer.meta.com/docs/develop/), [terms](https://wearables.developer.meta.com/docs/terms), and [acceptable use policy](https://wearables.developer.meta.com/docs/acceptable-use-policy).
- Record the access state of the Wearables docs, public MCP, and `llms.txt` endpoint separately. If a page requires login or cannot be fetched, record the gap; do not summarize its unseen contents.

## Fast path

Run the exact revision check and source-tree inventory first. If both are clean, emit a no-change receipt; if drift exists, compute impacted rows, routes, and packages, update only those, then rerun validators and archive parity.

## Refresh workflow

1. Run the bundled public-ref checker, source-tree inventory checker, and team-manifest validator, then record UTC/local date, URL, page title, repository commit/tag, release, retrieval method, and every expected/observed root AI file, plugin manifest, product, exact plugin-role name, sample, artifact, SDK, reference, example, template, and local-handoff result. A `DRIFT` result is a refresh blocker, not permission to silently rewrite the manifest.
2. Compare current sources with the prior snapshot for package products, minimum OS/toolchain, registration/permission rules, session lifecycle, camera/audio, Display/input, MockDevice, Web Apps, device models, terms, and release limitations.
3. For every changed symbol, write a migration note: old wording/API, new wording/API, affected role package, code-review action, and test fixture.
4. Reconcile iOS/Android/Web sources without treating platform parity as proof that symbols or behavior are identical; update the Android API atlas when artifact/API conflicts change.
5. Re-check product-generation mappings. Preserve `to-verify` when an official API/model enum or physical device is missing.
6. Update the registry and freshness log, then run local link/fence/whitespace/required-`## Sources` validation.
7. Report what was source-proven, what was locally build-proven, and what still needs an authenticated doc, account, or physical hardware.

## Current snapshot fields

At minimum, track:

- DAT iOS tag/commit and release date;
- DAT Android tag/commit when parity is being discussed;
- iOS minimum and sample toolchain;
- camera/audio/session/display/mock changes;
- Web App repository/docs commit and constraints;
- device enum/model/capability changes;
- preview/access/terms/publishing changes;
- unresolved “Gen 3,” “regular SDK,” MCP, and physical-device questions.
- product announcements versus SDK identity, and authenticated Developer Center
  access state;
- full-reference module names versus importable package products, HFP/A2DP/IMU availability, and current App Store/release-channel policy.
- upstream `AGENTS.md`/plugin examples versus versioned changelog/package guidance,
  including iOS/Android minimums, DAM metadata, and `Session`/`DeviceSession`
  names;
- Web App capability conflicts between the full Developer Center index and the
  toolkit `main`; preserve the revisions and carry text/offline/back/gesture/
  sensor behavior as `source-conflict`/`to-verify` until target evidence closes
  the gap.
- version-dependency and operational signals, including Meta AI/firmware
  prerequisites, on-glasses DAT-app update routes, Developer Mode versus
  release-channel behavior, and first-party versus community troubleshooting
  reports; keep access-gated values and issue reports separately labeled.

## Required output

- updated registry entries;
- freshness log row;
- changed-API/migration table;
- source-to-role impact map;
- operational compatibility/recovery impact map and first-party/community source classification;
- exact URLs and commits;
- access and evidence gaps;
- validation commands/results.
- public-ref checker output, including every expected and observed revision.
- source-tree inventory checker output, including every expected and observed product, exact role name/list, role count, sample, artifact, SDK, reference, example, and template count/value.
- team-manifest validator output, including local role count, upstream handoff count, and device-claim gate count.

## Hard boundaries

- Do not cite search snippets as the API contract when an official page or repository is available.
- Do not silently overwrite a previous source snapshot; preserve historical release notes.
- Do not infer a model mapping from a press release, and do not infer hardware support from an enum alone.
- Do not claim “full SDK coverage” while authenticated or unpublished docs, private preview behavior, or physical hardware remain unexamined.
- Do not resolve an official-source conflict by silently preferring a moving
  toolkit branch over a versioned/public Developer Center contract; record both
  and route the feature to the evidence packet.
- Do not copy upstream skill files wholesale; synthesize a source-linked local route and retain the upstream URL.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Transport and runtime reliability](../meta-wearables-transport-reliability/SKILL.md)
- [Debugging and observability](../meta-wearables-debugging-observability/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Apple source refresh](../ios-source-refresh-and-availability/SKILL.md)

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android API surface atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Meta Wearables terms](https://wearables.developer.meta.com/docs/terms)
- [Meta Wearables acceptable use policy](https://wearables.developer.meta.com/docs/acceptable-use-policy)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Wearables known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Wearables release-channel guidance](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/)
- [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/)
- [Ray-Ban Meta Gen 2 and Optics announcement](https://about.fb.com/news/2026/03/meta-ai-glasses-built-for-prescriptions/)
- [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
