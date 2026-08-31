# Meta Wearables source freshness log

Last review: 2026-08-30.

## Current records

| Route | Revision/date reviewed | Freshness status | Next trigger |
| --- | --- | --- | --- |
| DAT iOS | `main` `225f64ff1617e7acc8c407bb8d3ee132f7263d00`; 0.9.0 tag `9b1b83d791dfebff7afd452e924a256819094b64`; release 2026-08-03 | Current public repository snapshot; use the tag for reproducible package resolution and `main` for refresh-only signals. The moving-main DisplayAccess sample records iOS 17.2+, Xcode 26.4+, and Swift 6.3+. | New GitHub tag/commit, package upgrade, Xcode compile error, or Developer Center API change. |
| DAT Android | 0.9.0, commit `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc`, 2026-08-03 | Current public repository snapshot | New tag/Gradle artifact, API parity change, or Android sample change. |
| DAT Android API surface | Android `AGENTS.md`, upstream plugin skills, 0.9.0 changelog, official Android API reference, samples, and DAT-filtered reference reviewed 2026-08-22 | Four public Maven artifacts and the lifecycle/camera/Display/MockDevice/result/Flow lanes are mapped; upstream 0.8/`Session`/DAM examples remain source conflicts until the selected artifact compiles. | New Maven artifact/tag, generated API change, API-reference revision, compile result, or Android target migration. |
| Web Apps | `facebook/meta-wearables-webapp` main `a2714f862c61b1ce9c6cb624fc7e4938087102db`, reviewed 2026-08-30 | Current public toolkit snapshot after the repository relocation; the compare changed README, installer, and plugin metadata only, while exact Developer Center rules may require auth and the capability conflict remains open | Toolkit commit, Web App docs/MCP result, simulator update, target firmware, or physical device behavior change. |
| Public plugin surfaces | DAT iOS plugin `0.9.0` (10 skills), DAT Android plugin `0.9.0` (10 skills), Web Apps toolkit plugin `127.0.0` (12 skills), all reviewed at the repository revisions above | Current public routing/tooling snapshot; role coverage is not compile or hardware proof | Plugin manifest/repository change, package release, new toolkit role, or implementation request exposing an uncovered surface. |
| Full-SDK capability/conflict audit | iOS/Android `AGENTS.md`, plugin skills, samples, changelogs, Web Apps toolkit, and full reference reviewed at the revisions above | Current source inventory with explicit iOS/Android minimum-OS, DAM, version, session-name, audio, and Web Apps conflicts | Repository/changelog/API-reference change, target package resolution, MCP result, or a named device run that closes a conflict. |
| Product naming | Meta announcements through 2026-06 | Current consumer context, not SDK capability proof | New device/product announcement or support matrix update. |
| Device-generation/runtime mapping | DAT iOS/Android model-family sources, Gen 2/Optics announcements, Meta Glasses announcement, and Developer Center access check reviewed 2026-08-22 | Consumer label, SDK model identity, and runtime capability remain separate; “Gen 3” is `to-verify`; Developer Center compatibility tables are access-gated in this environment. | New model enum, authenticated support table, named runtime `DeviceType`, firmware/DAT version, or physical target run. |
| Version dependency and device compatibility | DAT iOS/Android 0.9.0 changelogs, Android package registry, full v0.9 reference, version-dependencies page, and public Gen 2 firmware report checked 2026-08-22 | Public release/artifact signals are available; the exact first-party version table is login-gated; the public firmware report is community evidence only. Compatibility tuples, firmware drift, Gen 2 capability results, and Gen 3 mapping remain target-specific. | Authenticated version table, new package/firmware/Meta AI/DAT-app release, official known issue, named runtime tuple, or physical compatibility run. |
| On-device compliance contract | DAT iOS/Android 0.9.0 changelogs, full reference, Web Apps toolkit, privacy route, and evidence packet reviewed 2026-08-22 | Processing location, raw-data, consent, thermal/lifecycle, network/storage, fallback, and evidence vocabulary are now explicit; “on-device” is not a blanket glasses-native claim. | New audio/sensor/processing API, policy change, privacy requirement, target build, named device run, or release-channel result. |
| Full-reference journey coverage | DAT-filtered `llms.txt?full=true&product=dat` section inventory rechecked 2026-08-22 | Setup/hardware/version dependencies, iOS/Android journeys, Display, lifecycle/permissions, HFP/A2DP, MockDevice, AI/MCP/tooling, organization/project/release channels, and Web Apps are now explicitly mapped to local owners. | New reference section, API/module, organization/release policy, MCP result, package compile, or target/device run. |
| Source-pinned surface manifest | Local schema `meta-wearables-public-surface-2026-08-22`, `manifest_revision: 6`, refreshed 2026-08-30 against the current source registry and official repository READMEs | Machine-readable journey/module/artifact/terminology/capability/conflict/generation/evidence/refresh inventory pins the upstream root AI files, lane plugin manifests, native-DAT local Codex install paths, Web Apps marketplace mode, and shared no-auth docs MCP tool split; it remains a routing snapshot rather than generated API or hardware proof. | Any source revision, package/artifact, full-reference wording, Web App runtime, agent install surface, MCP schema/auth statement, authenticated Developer Center result, model mapping, physical run, or evidence-ID change. |
| Agent team manifest | Local `meta-wearables-agent-team-2026-08-22`, `manifest_revision: 4`, refreshed 2026-08-30 | Exact 23-role local team, 32 upstream plugin-role handoffs, source AI surfaces, official agent-surface contract, shared handoff fields, and three device-claim gates are machine-validated against the source manifest and local package directories. | Any upstream role, local package, AI surface, Codex marketplace/plugin route, MCP tool/auth statement, capability owner, handoff field, source revision, device mapping, or evidence-contract change. |
| Terminology contract | Manifest `terminology_contract`, official DAT iOS/Android `AGENTS.md`, full reference, and Web Apps toolkit checked 2026-08-22 | “Regular SDK” is preserved as an ambiguous user phrase; “full SDK” is a composite audit; Ray-Ban Display is a native-DAT-or-WebApps route; Gen 2 is a product label with runtime gates; Gen 3 remains an unresolved alias. | Official SDK/product terminology, support/model mapping, authenticated Developer Center table, selected package/API, or named-device result changes. |
| Repository/package tree inventory | iOS 0.9.0 `Package.swift`/tag tree, Android 0.9.0 sample catalogs, and Web Apps main toolkit tree checked 2026-08-30 | iOS has five package products including test-only `MWDATMockDeviceTestClient`; Android has four DAT artifacts with sample SDK levels 31/36/36 and two sample roots; the exact ten iOS, ten Android, and twelve Web Apps role names are pinned and checked alongside the recorded references/examples/templates. | New Package.swift product, XCFramework, Maven coordinate, plugin role/name, sample root, SDK level, Web App reference/example/template, or source-tree revision. |
| Version-pinned API surface register | Local `meta-wearables-api-surface-2026-08-22`, 30 rows normalized from the reviewed DAT iOS/Android changelogs, API-reference links, full reference, and Web Apps toolkit/docs | Agent-facing symbol/artifact rows now carry source anchors, status, compile/runtime gate, privacy path, fallback, and migration notes; no row promotes source evidence to compile or physical proof. | Any changelog/API/reference/toolkit revision, selected artifact signature, source conflict, package build, target runtime, privacy path, or evidence-level change. |
| Operational readiness and recovery | DAT iOS/Android 0.9.0 changelogs, raw DAT-filtered reference, version-dependency/known-issue/release entry points, and public troubleshooting signals reviewed 2026-08-22 | Compatibility tuple, Developer Mode/release-channel boundary, companion/firmware/on-glasses-DAT-app provisioning, thermal/power/lifecycle recovery, and attempted-versus-observed recovery are now explicit. Raw reference prerequisites and access-gated/current version tables remain separate; community reports are troubleshooting signals only. | New SDK/firmware/Meta AI version, version-dependency table, provisioning API/error, official known issue, release-channel policy, or named target recovery run. |
| Public repository/ref checker | Bundled `check_source_revisions.py` run 2026-08-30 against the refreshed surface manifest | iOS `main`, iOS tag `0.9.0`, Android `main`, Web Apps `main`, and five full-reference anchor terms all matched; `CHECKS 5 DRIFT 0`. | Run before every source-sensitive implementation; `DRIFT` requires a new receipt and impact audit, not an automatic manifest rewrite. |
| Public source-tree inventory checker | Bundled `check_source_tree_inventory.py` run 2026-08-22 against the surface manifest; the credential-free checker now falls back from GitHub Contents API 403/429 responses to a read-only codeload archive | All 23 checks matched: the three shared root AI files for each lane, iOS five products/five XCFrameworks, exact ten role names, two samples, and toolchain; Android exact ten role names, two samples, four artifacts, and 31/36/36 SDK tuple; Web Apps exact twelve role names, two references, `snake`, and `prompts.json`. | Run after every ref check; any root AI file, plugin manifest, product, role/name, sample, artifact, SDK, reference, example, template, or plugin-version drift requires a source receipt and manifest impact review. |
| Application architecture and platform boundaries | DAT iOS/Android 0.9.0 module/changelog contracts, Web Apps toolkit/full-reference boundary, on-device/recovery routes, and evidence packet reviewed 2026-08-22 | Shared product state, platform-specific adapter ownership, native Display/Web App separation, phone fallback, session epochs, cancellation, bounded media, stale-event rejection, and layered evidence are now explicit. | New module/API/lifecycle semantics, platform-parity change, Web App runtime contract, package compile, or named target architecture/build review. |
| Developer Center operations | DAT-filtered reference, onboarding/organization management, manage projects, release channels, and telemetry sections reviewed 2026-08-22 | Organization/team/project/app identity, version/build, channel/tester, telemetry, and recovery ownership are now explicit; authenticated account and channel state remains access-gated and no destructive operation is authorized by the source pass. | New Developer Center flow, account policy, version/build status, channel rule, telemetry key, or authorized project run. |
| Transport and runtime reliability | DAT iOS/Android 0.9.0 changelogs, iOS/Android setup routes, DAT-filtered reference, Apple local-network/audio docs, and Android Bluetooth permission docs reviewed 2026-08-22 | iOS Wi-Fi transport and local-network/Bonjour setup are source signals; Android Bluetooth/Internet setup is source-backed but an equivalent DAT Wi-Fi contract remains `to-verify`; HFP/A2DP, queue, thermal, and recovery ownership are now explicit. | New transport/API signal, artifact parity documentation, local-network requirement, audio route, firmware behavior, package compile, or named physical transport run. |
| Debugging and observability | Official iOS/Android `debugging` and `live-debugging-mcp` roles re-read at current `main` revisions, plus direct DAT MCP endpoint and current raw reference access check on 2026-08-22 | Read-only DAT Inspector/MCP baseline, companion-boundary/device-path diagnosis, narrow event waits, typed errors, and redacted diagnostic export are now a dedicated role and evidence lane; direct shell retrieval of the raw reference succeeded while interactive web retrieval rendered a login gate. | New debug tool/API, MCP schema, repository role, known issue, SDK/build error, target debug server, or redacted diagnostic bundle. |
| Input, sensors, and physical interaction | Full reference, DAT iOS/Android Display skills, Web Apps `AGENTS.md`/Display guidance, Core Motion/Location fallback references reviewed 2026-08-22 | Native Display action guidance is source-backed; the public native repository snapshot does not establish a dedicated IMU/EMG/temple API; Web App D-pad/EMG and browser sensor guidance remains feature-level source-conflict/to-verify; normalized event epoch, privacy, teardown, and INP evidence rows are now explicit. | New native sensor symbols/artifacts, authenticated Web App contract, toolkit/runtime change, simulator result, target firmware, physical input/sensor run, or release-channel result. |
| Security, attestation, and credential boundaries | Full reference, DAT iOS/Android getting-started and permissions/registration roles, Developer Center project/release pages, Apple ExternalAccessory/privacy-manifest/App Store sources reviewed 2026-08-22 | iOS/Android identity tuples, callback ownership, Developer Mode versus release attestation, package/signing credential redaction, Web App origin separation, dated App Store warning, and SEC evidence rows are now explicit; account, secret values, attestation, signing, physical, and production state remain unverified. | New identity key, attestation behavior, Developer Center policy, package access flow, Apple review requirement, target build, channel result, or security incident. |
| Preview/publishing | Meta announcement, README, Developer Center entry points | Policy-sensitive; verify per project/account | Release-channel or public-eligibility change. |

## 2026-08-22 live refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| DAT iOS repository and `CHANGELOG.md` | Public GitHub pages/raw files plus `git ls-remote` | 0.9.0 camera child/stop route, Display `ButtonGroup`, listener bag, `supportsDisplay`, crash opt-out, iOS 17.2 minimum, MockDevice link checks, stream completion and error changes; `main` and tag have distinct commits. | Source-proven migration guidance; pin the tag for a target and recompile before using symbols. |
| DAT Android repository | Public GitHub page/raw file plus `git ls-remote` | Current public main snapshot `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc`. | Source snapshot only; do not infer Kotlin/Swift parity without the selected artifact. |
| Full Wearables reference `llms.txt?full=true` | Public HTTPS retrieval | v0.9 module/device/audio/Web Apps index, HFP/A2DP ordering, MockDevice guidance, preview/release and App Store warning; iOS minimum/module naming conflict remains. | Use as public platform index; reconcile version-sensitive claims with package/changelog/API reference. |
| Web Apps toolkit `AGENTS.md`, display/performance guidance | Public raw GitHub files plus `git ls-remote` | `main` `24d7bfc...` documents text composer, offline/service-worker, Escape/back, gestures, sensors, 600×600/additive/performance rules. | Official but moving toolkit guidance; record text/offline/back/gesture/sensor as source-conflict/to-verify against Developer Center, MCP, simulator, firmware, and physical MRBD. |
| DAT iOS/Android and Web Apps plugin manifests/skills | Public repository inspection at the same commits | Confirmed the upstream role inventory: iOS/Android ten-role plugin surfaces plus twelve Web Apps toolkit roles. | Routing evidence only; the local team must still pin target artifacts and preserve platform-specific APIs. |
| DAT iOS/Android `AGENTS.md` and plugin examples versus 0.9.0 changelogs | Public raw files at the same commits | Found stale/conflicting iOS minimum, Android/iOS DAM metadata, Android 0.8.0 example version, and Android `Session`/`DeviceSession` naming guidance. | Preserve as source-conflict/stale-upstream guidance; resolve against the selected package/API reference and target build. |
| Web Apps Developer Center and MCP entry points | URL/access check; no private account state asserted | Public route remains an access-sensitive authority surface. | Do not treat an inaccessible/authenticated page as confirmation; refresh with project access when implementing. |

## 2026-08-30 Web Apps repository relocation receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| Web Apps repository | `git ls-remote --refs` plus the public GitHub compare from the prior pinned commit | `facebook/meta-wearables-webapp` `main` resolves to `a2714f862c61b1ce9c6cb624fc7e4938087102db`; the one-commit compare changes `README.md`, `install-skills.sh`, and `.cursor-plugin/plugin.json` only. README/install/plugin metadata now use the `facebook` owner and the simulator name is updated. | Source/routing refresh only; no API/runtime row changed. Keep the toolkit capability conflicts as `source-conflict`/`to-verify`, update canonical URLs and pins, and rerun the ref/tree/package validators. |
| Local source contracts | Refreshed surface/team manifests and target-intake records | Surface `manifest_revision: 6`, team `manifest_revision: 4`, Web Apps short revision `a2714f8`, and canonical repository URLs are machine-checked. | Source evidence only; no target build, account, connected-device, physical, signing, or release claim is promoted. |

## 2026-08-22 security and attestation refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| Full Wearables reference `llms.txt?full=true` | Direct HTTPS shell retrieval and focused keyword excerpts | Developer Mode registration, iOS `AppLinkURLScheme`/`MetaAppID`/`ClientToken`/`TeamID`, Android `APPLICATION_ID`/`CLIENT_TOKEN`, attestation behavior, release-channel identity, one-app Developer Mode registration note, and current DAT App Store warning. | Source evidence only; resolve the selected package/build/account and recheck dated Apple/Meta review gates. |
| DAT iOS getting-started and permissions/registration roles | Direct raw GitHub retrieval at iOS `main` `225f64ff...` | Info.plist callback configuration, Developer Mode `MetaAppID` placeholder, Meta AI URL callback, registration/permission states, and Developer Mode versus production table. | Source/role evidence; do not expose values or call callback receipt registration/attestation proof. |
| DAT Android getting-started and permissions/registration roles | Direct raw GitHub retrieval at Android `main` `81dfb51b...` | GitHub Packages `read:packages` access, manifest placeholders, callback intent filter, Android identity values, and Developer Mode/release distinction. | Source/role evidence; keep package tokens separate from project credentials and resolve the exact artifact. |
| Apple ExternalAccessory, privacy manifest, and App Store review entry points | Official Apple documentation links recorded for recheck | Apple review/framework boundary relevant to Meta's dated DAT App Store warning. | Current Apple review remains a separate authority; do not claim approval or permanent ineligibility from one Meta snapshot. |

This receipt is a source refresh, not a target build, account, attestation,
signed artifact, connected-device, physical, App Store/Play, or production
result.

## 2026-08-22 debugging and observability refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| DAT iOS `debugging` and `live-debugging-mcp` roles | Direct raw GitHub retrieval at `main` `225f64ff...` | Developer Mode/version/session diagnosis; read-only server discovery, connection/readiness baseline, companion boundary, device path, narrow waits, errors/digest, and diagnostic export. | Source/role evidence; run against a named app debug server only when available. |
| DAT Android `debugging` and `live-debugging-mcp` roles | Direct raw GitHub retrieval at `main` `81dfb51b...` | Android initialization/manifest/build-mode/`DatResult` diagnosis plus the same app-visible live-debugging sequence with Android state names. | Source/role evidence; do not infer iOS symbols or target readiness. |
| Wearables MCP and raw full reference | Direct HTTPS shell retrieval plus interactive web open | Raw endpoint currently returns the v0.9 product split and API index; interactive web retrieval may render `Not Logged In`. | Preserve client/access distinction; docs lookup is not a local debug server, account state, compile, or physical proof. |
| DAT iOS/Android Display roles plus Web Apps input/sensor guidance | Direct raw GitHub retrieval at current `main` commits and full-reference shell retrieval | Native Display `Button`/`ButtonGroup`/tap guidance, Web App D-pad/EMG/focus and browser sensor guidance, and full-reference IMU/Web Apps capability wording were compared; no dedicated native IMU/EMG/temple package role was found in the public DAT trees. | Route native sensor symbols to `to-verify`; keep Web App text/offline/back/gesture/sensor rows source-conflicted; require browser, connected, physical, and release evidence independently. |

## 2026-08-22 device-generation refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/) and [Gen 2 Optics announcement](https://about.fb.com/news/2026/03/meta-ai-glasses-built-for-prescriptions/) | Official Meta newsroom search/open | Meta publicly uses Gen 2 and Gen 2 Optics product names. | `source` naming only; do not infer DAT artifact support or Display capability. |
| [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/) | Official Meta newsroom search/open | A separate 2026 Meta Glasses product line is named; the announcement does not establish a third-party DAT `DeviceType` mapping. | `source` naming only; keep any user “Gen 3” alias `to-verify`. |
| DAT iOS/Android GitHub trees and changelogs | GitHub API tree inspection plus official repository pages | DisplayAccess, MockDevice, and model-family source surfaces are present; no public file inspected establishes “Gen 3” as a runtime label. | `SDK`/source inventory; inspect the selected package/artifact and named target next. |
| [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/) and [full reference](https://wearables.developer.meta.com/llms.txt?full=true) | Interactive page plus direct raw HTTPS retrieval | The interactive Developer Center rendered a login-gated surface; the raw full-reference and DAT-filtered endpoints returned readable v0.9 source text, including the broader conceptual index, Gen 1/Gen 2/Optics/Display hardware list, and HFP/A2DP notes. | `source` for the raw index; `access-gated` for authenticated compatibility/version-dependency/policy tables. Reconcile with the selected package/changelog and do not treat the index as physical proof. |

This refresh changes product-name routing and evidence requirements only. It is
not a build, account, connected-device, physical-glasses, or release result.

## 2026-08-22 version-dependency and device-compatibility refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| DAT iOS and Android changelogs | Official public GitHub pages/raw files | Both public repositories identify 0.9.0 on 2026-08-03; iOS and Android 0.9 migration facts remain version-sensitive. | `source`; pin the selected package/artifact and compile the target. |
| Android package registry | Official public GitHub Packages pages | `mwdat-core`, `mwdat-camera`, and related public artifacts expose 0.9.0 versions. | Artifact availability only; resolve credentials and the target dependency graph separately. |
| Wearables version-dependencies page | Official URL opened through the web surface | Page returned `Not Logged In`. | `access-gated`; do not reconstruct exact app/firmware values from snippets or memory. |
| DAT iOS issue #265 | Public GitHub issue page | Closed community report describes a Gen 2 126→127 session failure on 0.9.0; no official support conclusion is established by the report. | `community-signal`; use as a refresh/tuple-recording trigger, not as policy. |

This receipt is source/access evidence only. It is not a package compile, account,
connected-device, physical, release-channel, or Gen 3 result.

This receipt is a source refresh, not a build, account, connected-device, or
physical-glasses result.

## 2026-08-22 official agent-surface refresh receipt

| Source | Retrieval/method | Signal captured | Classification and next action |
| --- | --- | --- | --- |
| [DAT iOS README](https://github.com/facebook/meta-wearables-dat-ios#readme) | Official GitHub README opened at current `main` | The repository publishes Codex/Claude/Copilot/Cursor/AGENTS.md surfaces, documents `codex plugin install ./plugins/mwdat-ios` and `./install-skills.sh codex`, and points to the shared no-auth Wearables MCP with `search_dat_docs`. | First-party agent/tooling source only; install from a reviewed checkout and resolve the selected DAT package/API separately. |
| [DAT Android README](https://github.com/facebook/meta-wearables-dat-android#readme) | Official GitHub README opened at current `main` | The Android README documents the four 0.9.0 artifacts, the local Codex plugin route `./plugins/mwdat-android`, the `./install-skills.sh codex` helper, and the same no-auth MCP/`search_dat_docs` route. | First-party Android agent/tooling and dependency source; never print the required GitHub Packages token or treat README setup as a target compile. |
| [Web Apps README](https://github.com/facebook/meta-wearables-webapp#readme) | Official GitHub README opened at current `main` | The Web Apps toolkit exposes Codex marketplace installation, `install-skills.sh` fallback, the shared no-auth MCP with `search_webapps_docs`, and the separate browser/public-HTTPS/physical route. | First-party Web Apps agent/tooling source; retain the native DAT/Web Apps boundary and use browser/connected/physical evidence independently. |
| [Wearables MCP](https://mcp.developer.meta.com/wearables) | Endpoint recorded from all three official READMEs; this workspace client capability checked locally | Public docs lookup is an upstream source route, but this workspace currently cannot call the MCP. | Route receipts retain `local_callable=false`; use pinned repository files or full reference as fallback and never promote docs lookup to runtime/device proof. |

This refresh changes the machine-readable agent-surface contract and routing
receipt only. It does not change the DAT package products, Web Apps runtime,
device-generation mapping, account state, physical behavior, or release proof.

## Historical API traps to search for

- `DeviceSession.addStream(config:)` versus current `addCamera(config:)` and
  `camera.stream`.
- `StreamSession`, `StreamSessionConfig`, and `StreamSessionState` versus the
  current names.
- old DAM opt-out keys versus 0.9.0 always-on behavior.
- `pairRaybanMeta()` versus `pairGlasses(model:)`.
- `CaptureError` versus current stream error handling.
- assumptions that a browser arrow-key or MockDevice tap equals a real
  Neural Band/captouch interaction.
- assumptions that “Gen 3” equals `.metaGlasses`, `.rayBanMeta`, or Display.

## Refresh receipt

For each future update, append a row or link a durable receipt containing the
signal, official source, repo/package revision, target/toolchain, affected
pages/packages/fixtures, commands, evidence level, uncertainty, and next
trigger. Preserve historical entries; do not silently rewrite an old API into a
current claim.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Official Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Meta Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Meta Wearables MCP](https://mcp.developer.meta.com/wearables)
