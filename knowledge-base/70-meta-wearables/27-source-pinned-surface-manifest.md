# Source-pinned Meta Wearables surface manifest

This route makes the “full SDK” claim inspectable by agents and humans. The
portable [surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
is a machine-readable snapshot of the public DAT iOS, DAT Android, native
Display, Web Apps, phone-fallback, capability, conflict, generation, and
evidence surfaces reviewed on 2026-08-22.

It is a routing manifest, not a generated API reference or hardware support
table. The exact selected package/artifact and target runtime always outrank it.

Use the companion [agent-team roster and handoff contract](30-agent-team-roster-and-handoff-contract.md)
to map each selected upstream plugin role to a local owner and device-claim gate.

## What the manifest covers

| Layer | Manifest fields | Local authority |
| --- | --- | --- |
| Product journeys | Native DAT iOS, native DAT Android, Web Apps, and phone fallback | [route selection](00-platform-and-route-selection.md) |
| Mobile modules/artifacts | Five iOS package products (four runtime products plus `MWDATMockDeviceTestClient`), four Android Maven artifacts, and iOS index-only conceptual names | [iOS atlas](10-dat-ios-api-surface-atlas.md), [Android atlas](20-dat-android-api-surface-atlas.md) |
| Source-tree inventory | iOS Package.swift/plugin/sample anchors, Android plugin/sample/artifact/SDK anchors, and Web Apps plugin/reference/example/template anchors | [upstream skill/tooling map](11-upstream-skill-and-tooling-map.md), [source refresh role](../skills/packages/meta-wearables-source-refresh/SKILL.md) |
| Agent surfaces | Per-lane root `AGENTS.md`, `README.md`, and `install-skills.sh`, each `.codex-plugin/plugin.json`, native-DAT local Codex installs, Web Apps marketplace install, and the no-auth docs MCP tool split | [upstream skill/tooling map](11-upstream-skill-and-tooling-map.md), portable `agent_surface_contract` |
| Terminology contract | Machine-checked resolution for “regular SDK,” “full SDK,” Ray-Ban Display, Gen 2, and Gen 3 wording | [device-generation matrix](16-device-generation-and-runtime-support-matrix.md), [portable manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml) |
| API surface rows | 30 normalized iOS, Android, Web Apps, and conceptual-index rows with symbols, source anchors, status, gates, privacy path, fallback, and migration notes | [iOS atlas](10-dat-ios-api-surface-atlas.md), [Android atlas](20-dat-android-api-surface-atlas.md), [Web Apps route](06-web-apps-display-and-input.md) |
| Capabilities | Registration, sessions, camera/photo, audio, native Display, Web Apps, sensors, MockDevice, debug, privacy, identity, compliance, and compatibility | [full-SDK matrix](15-full-sdk-capability-and-source-conflict-matrix.md) |
| Capability/evidence plan | Machine-readable owner roles, implementation route, privacy path, fallback, required evidence levels, preflight tasks, and proof task IDs for all 14 capabilities | [portable plan](../skills/packages/meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml) |
| Conflicts | Minimum OS, DAM/camera lifecycle, Android naming, Web App features, Android Wi-Fi parity, and version-table access | [source refresh log](09-source-refresh-and-version-history.md) |
| Product labels | Gen 2, Gen 2 Optics, Display, Meta Glasses, Gen 3, and “regular SDK” | [device-generation matrix](16-device-generation-and-runtime-support-matrix.md) |
| Evidence | Source through production ladder, route-specific `*` evidence IDs, and mapped target-preflight `PRE-*` tasks | [evidence packet](12-device-and-release-evidence-packet.md), [target preflight](../skills/packages/meta-wearables-device-proof/references/target-preflight.md) |
| Team ownership | 23 local roles, 32 upstream role handoffs, shared handoff fields, and Ray-Ban Display/Gen 2/Gen 3 claim gates | [team manifest](../skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml), [team validator](../skills/packages/meta-wearables-agentic-team/scripts/validate_team_manifest.py) |

## Agent loading protocol

1. Load the manifest before answering a “full SDK,” “all capabilities,” parity,
   Gen 2/Gen 3, or “regular SDK” request.
2. Resolve the requested wording through `terminology_contract`; preserve
   `ambiguous-user-phrase`, `composite-audit`, `capability-and-product-label`,
   `product-label-with-runtime-gate`, or `unresolved-alias` status before choosing
   a route.
3. Select the journey and platform-specific atlas; do not translate symbols by
   name.
4. Filter `api_surface.rows` by journey/platform/lane and load each row’s source
   anchors, status, compile/runtime gate, privacy path, fallback, and migration
   note before writing implementation guidance.
5. Filter capabilities by the requested surface and preserve each status:
   `source-backed`, `device-gated`, `source-conflict`, `to-verify`, or
   `access-and-physical-gated`.
6. Read `preflight_contract`, map each selected capability to its `PRE-*`
   tasks, and carry each task as `not-run`, `static`, `build`, `mock`,
   `browser-sim`, `connected`, `physical`, `signed`, `release-channel`, or
   `production`. Preflight freezes facts; it does not promote evidence.
7. Resolve the exact package/artifact/API reference and target configuration;
   the manifest never replaces compilation or generated API inspection.
8. Load `agent_surface_contract` before using upstream agent instructions:
   local-install native DAT plugins from the selected checkout, use the Web Apps
   marketplace route for that lane, and use the no-auth MCP endpoint only for
   current docs lookup when the client supports it. Otherwise use the pinned
   repository/full-reference fallback.
9. Attach the listed evidence rows and return unsupported/unverified fallbacks.
10. Validate the capability/evidence plan and carry its owner, implementation,
   privacy, fallback, minimum-level, and proof-task fields into the specialist
   handoff.
11. Record any source or runtime change as a freshness-log receipt and update
   the manifest revision rather than silently rewriting a prior claim.

## API row status semantics

| Status family | Meaning | Next proof |
| --- | --- | --- |
| `source-confirmed` / `public-artifact` | The official snapshot names the module, artifact, symbol, or behavior | Resolve the exact target package/API and compile it when implementation is in scope. |
| `source-conflict` / `*-versioned` | Sources or release generations disagree, or the row is migration-sensitive | Pin the release, compare the changelog/API, and run a target compile/fixture. |
| `*-to-verify` / `package-resolution-required` | The exact contract, package exposure, or route is not established | Reopen the selected reference/artifact or keep the typed fallback. |
| `*-device-gated` / `physical-and-release-gated` | Source coverage exists, but capability, firmware, target, or channel behavior needs a named run | Execute the connected/physical/signed/release task and preserve the tuple. |
| `*-test-only` | Mock or browser tooling can prove deterministic logic or layout only | Keep hardware, optics, audio, firmware, and physical input claims separate. |

## Non-negotiable interpretation rules

- Four runtime DAT module/artifact lanes are the current public mobile capability
  inventory, with the iOS package adding the test-only
  `MWDATMockDeviceTestClient`; broader names in the full reference remain
  package-resolution gates.
- Native DAT and hosted Web Apps are separate product journeys. “Regular SDK”
  is an unresolved user phrase until routed to one of them.
- Gen 2 is a source-level product/runtime candidate, not universal firmware or
  capability proof. Gen 3 remains `to-verify`.
- The Web Apps toolkit/full-reference conflict remains feature-level; do not
  promote text input, offline, back, extended gestures, or sensors to supported
  without target evidence.
- Source, static, build, mock, browser, connected, physical, signed, channel,
  and production evidence cannot be substituted for one another.
- Target preflight can establish a reproducible target/dependency/identity/data
  path, but it cannot establish compile success, device behavior, account
  authorization, physical Display/audio/input behavior, or release eligibility.
- No credentials, raw media, private project identifiers, tester data, or
  unredacted device identifiers belong in the manifest or archive.

## Maintenance

The manifest is maintained with the [Meta source registry](../sources/meta-wearables-source-registry.md),
[freshness log](../sources/meta-wearables-source-freshness-log.md), and
[source-refresh role](../skills/packages/meta-wearables-source-refresh/SKILL.md).
Keep the mapped [target-preflight packet](../skills/packages/meta-wearables-device-proof/references/target-preflight.md)
and `PRE-*` task IDs aligned with the manifest capability rows.
The current `manifest_revision` is `6`; increment it when the machine-readable
source or terminology contract changes without changing the public snapshot date.
Run the bundled [manifest validator](../skills/packages/meta-wearables-full-sdk-audit/scripts/validate_surface_manifest.py)
and [capability/evidence-plan validator](../skills/packages/meta-wearables-full-sdk-audit/scripts/validate_capability_evidence_plan.py)
after edits and before rebuilding the portable archive. When a revision changes,
update the YAML snapshot, affected route/package owners, source-conflict rows,
capability/evidence-plan entries, evidence IDs, and the refresh receipt together.

## Sources

- [Portable source-pinned surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS AGENTS.md](https://github.com/facebook/meta-wearables-dat-ios/blob/main/AGENTS.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Web Apps AGENTS.md](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
