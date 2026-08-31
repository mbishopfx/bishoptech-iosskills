# Source refresh and version history

Meta Wearables is moving quickly and the public API is developer-preview
quality. Refresh this lane from the primary sources before every new app route,
package upgrade, hardware claim, or publishing decision.

## Refresh workflow

1. Capture the signal: release tag, changelog entry, API-reference change,
   Developer Center notice, sample diff, firmware/app compatibility change,
   Web App display rule, preview/publishing policy, or observed device error.
2. Reopen the official DAT iOS/Android repository, exact API page, official Web
   App toolkit/reference, and relevant Meta product/policy source.
3. Inspect the installed Swift package or Android artifact and the actual target
   configuration when a signature, minimum OS, manifest/Info.plist key, or
   capability is involved.
4. Search this lane, the role packages, source registry, fixtures, catalogs, and
   GoalBuddy receipts for the symbol, URL, model name, or old claim.
5. Classify each hit as `current`, `historical`, `ambiguous`, `to-verify`,
   `device-gated`, `account/channel-gated`, or `unsupported`.
6. Update only the affected route and package, preserve history, rerun link and
   package checks, and record the next trigger.

Before treating the pinned repository revisions as current, run the portable
[public-ref checker](../skills/packages/meta-wearables-source-refresh/scripts/check_source_revisions.py):

```bash
python3 ../skills/packages/meta-wearables-source-refresh/scripts/check_source_revisions.py
```

It checks the public iOS, Android, and Web Apps `main` refs plus the exact iOS
reproducible release tag recorded in the [surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml).
`DRIFT` means the source snapshot needs a new receipt and impact audit; it does
not authorize an automatic manifest rewrite.

Then run the [source-tree inventory checker](../skills/packages/meta-wearables-source-refresh/scripts/check_source_tree_inventory.py)
to verify the pinned Package.swift products, plugin versions/exact role names
and counts, sample roots/toolchains, Android artifacts, and Web Apps
references/examples/templates.

When upstream role names or local owners change, also run the [team-manifest
validator](../skills/packages/meta-wearables-agentic-team/scripts/validate_team_manifest.py)
against the [source-pinned manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
and workspace role directories before delegating implementation.

For a request that says “full SDK,” “regular SDK,” or “all capabilities,” use
the [full SDK capability and source-conflict matrix](15-full-sdk-capability-and-source-conflict-matrix.md)
and the manifest `terminology_contract`. Preserve “regular SDK” as an
ambiguous phrase until the intended native DAT or Web Apps surface is explicit.
It records upstream `AGENTS.md`/plugin guidance that is stale or conflicts with
the versioned 0.9.0 changelogs, including minimum OS, DAM metadata, and
`Session`/`DeviceSession` naming.

## Version history owned by this tranche

| Signal | Current snapshot | Meaning |
| --- | --- | --- |
| DAT 0.9.0, 2026-08-03 | iOS and Android official repositories | Camera is consolidated under `Camera`; Display `ButtonGroup` exists; DAM opt-out is removed/always enabled; iOS minimum is 17.2. |
| DAT 0.8.0, 2026-06-25 | Current historical route | Added Meta Glasses/model enum, multi-glasses MockDevice, Wi-Fi, Display clear; older direct capability shape is not current. |
| DAT 0.7.0, 2026-05-14 | Historical Display introduction | Added Display, DAM, captouch simulation, device health/update routes; do not use 0.7 names in a 0.9 app without a compatibility note. |
| Web Apps toolkit main | Commit `a2714f862c61b1ce9c6cb624fc7e4938087102db`, reviewed 2026-08-30 after the repository move to `facebook/meta-wearables-webapp` | The 2026-08-30 compare contained README, installer, and plugin-metadata relocation changes only; the 600x600 additive display, D-pad/EMG focus, HTTPS delivery, browser simulator, text composer, offline/service-worker, Escape/back, gesture, sensor, and performance guidance remain toolkit claims, with conflicts still `to-verify`. |
| Wearables `llms.txt?full=true` | Public `v0.9` reference reviewed 2026-08-22 | Expands the public surface map with HFP/A2DP audio, IMU/Web App capabilities, MockDevice test-server guidance, MCP/tool integrations, release-channel policy, version dependencies, and current App Store warning; reconcile its iOS minimum and module names against the pinned package. |
| Product/generation refresh, 2026-08-22 | Official Meta Gen 2, Gen 2 Optics, Meta Glasses, and Display announcements plus DAT model-family sources | Consumer product labels are current source evidence, not runtime support mappings. The interactive Developer Center UI is login-gated, while the raw full-reference endpoint is readable v0.9 source text; “Gen 3” remains `to-verify`. |
| Operational-readiness refresh, 2026-08-22 | Raw DAT reference Display prerequisites, version-dependency/known-issue/release entry points, 0.9.0 changelogs, and public troubleshooting signals | Keep companion/firmware/on-glasses-DAT-app provisioning, Developer Mode versus release channel, update-required, thermal/power, and recovery claims in a separate operational packet. Access-gated tables and issue reports do not close physical recovery evidence. |

## Required refresh record

```text
signal:
official_sources:
repository_commit_or_package_version:
target_os_sdk_toolchain:
device_model_firmware_meta_ai_version:
old_claim:
classification:
new_claim:
affected_pages_packages_fixtures:
commands_and_results:
evidence_level:
unverified_boundary:
next_refresh_trigger:
```

## Current uncertainties

- The interactive/authenticated Developer Center API and compatibility tables
  were not accessible in this session. The raw full-reference and DAT-filtered
  `llms.txt` endpoints were readable as public v0.9 source text, but exact
  version-dependency values and account/policy gates still require the logged-in
  Developer Center or an authorized public Wearables MCP result.
- “Gen 3” is not a current official public DAT enum label in the reviewed
  sources. Resolve it from the actual device metadata, current product/support
  documentation, and a physical pair before adding a mapping.
- The raw Display guide includes companion/firmware and Developer Mode
  prerequisites, while current version-dependency values may require an
  authenticated view. Record both the raw snapshot and the selected account
  result; never treat a public issue report as an official support guarantee.
- Consumer Meta AI features and third-party DAT/Web App capabilities are not the
  same surface. Do not infer access to “Hey Meta,” private Meta AI behavior,
  neural-band signals, or background audio from this SDK lane.

## Open Web Apps source conflict

The full public reference currently says Web Apps have no text input, offline
support, or back navigation (and also lists no camera, microphone, or
notifications). The official toolkit `main` snapshot documents an on-glasses
HTML-field composer, service-worker/offline patterns, Escape/back, extended
gestures, and Generic Sensor API guidance. Preserve both observations with
their revisions. A Web App feature is not implementation-ready until the exact
runtime, authenticated docs/MCP result, simulator build, and physical MRBD run
agree or the product chooses the phone/manual fallback.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS tags and releases](https://github.com/facebook/meta-wearables-dat-ios/tags)
- [Official DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [Official Meta Wearables MCP server](https://mcp.developer.meta.com/wearables)
- [Official Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Meta Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Wearables known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Wearables release-channel setup](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/)
