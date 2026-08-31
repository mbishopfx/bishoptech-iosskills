---
name: meta-dat-api-atlas
description: Map and refresh the public Meta DAT iOS API surface, upstream role skills, sample apps, MCP/docs tooling, configuration keys, and DAT-versus-Web-Apps boundary without inventing release-specific symbols. Use when an implementation needs exact MWDAT modules, current 0.9 migration details, debugging tools, or broader SDK coverage.
---

# Meta DAT API atlas

Use this role before writing a version-sensitive DAT import, migration, sample
architecture, debugging plan, or claim that the “full SDK” supports a feature.
It is the source/API librarian for the Meta team, not a substitute for compiling
the selected package.

## Read before acting

- Inspect the real target’s package graph, resolved version, deployment target,
  Info.plist, entitlements, privacy manifest, test targets, and existing DAT
  adapter.
- Read [the DAT API surface atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md),
  [the upstream skill/tooling map](../../../70-meta-wearables/11-upstream-skill-and-tooling-map.md),
  [the public plugin and skill matrix](../../../70-meta-wearables/13-public-plugin-and-skill-matrix.md),
  [the DAT Android parity route](../../../70-meta-wearables/14-dat-android-parity-and-boundaries.md),
  [the full SDK capability/conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md),
  [the source-pinned surface manifest](../../../70-meta-wearables/27-source-pinned-surface-manifest.md),
  and [the surface fixture](references/surface-map.md).
- Load the iOS `api_surface.rows` from the portable [source-pinned manifest](../../../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
  for normalized symbol/status/gate/fallback rows; use the pinned package and
  generated API to resolve any signature conflict.
- Refresh the official [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios),
  [README](https://github.com/facebook/meta-wearables-dat-ios#readme),
  [0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md),
  [full `llms.txt` reference](https://wearables.developer.meta.com/llms.txt?full=true),
  [iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest),
  and [Wearables MCP](https://mcp.developer.meta.com/wearables).
- Read the relevant local Apple route for Swift Package Manager, AVFAudio,
  ExternalAccessory, privacy, testing, and physical-device release proof.

## Atlas workflow

1. Freeze the source snapshot: repository commit/tag, changelog release, API
   reference URL, `llms.txt` retrieval date, and MCP query if used. Keep a
   moving `main` commit distinct from the reproducible package tag.
2. Map the public module/product names to the exact package products exposed by
   the target. Mark machine-index-only names `to-verify`.
3. Trace the route from `Wearables.configure()` through registration, callback,
   permission, device selection, session, capability, stream/display state,
   teardown, and fallback.
4. Map camera/photo, HFP/A2DP audio, Display DSL/input/video, IMU, MockDevice,
   sample, and debugging surfaces separately. Record source conflicts such as
   optional signatures or stale minimum-OS prose.
5. Compare DAT native mobile and Web Apps as distinct product journeys. Resolve
   “regular SDK” language to an official route or leave it `to-verify`. When the
   Web App toolkit and full-reference index disagree, preserve both revisions
   and route the feature to the device-proof packet.
6. Return exact source links and implementation/test implications without
   copying upstream skill prose or exposing credentials/media.

## Fast path

Answer an exact-symbol request with one normalized row: source revision, package/module, symbol, status, target gate, fallback, and proof. Expand to the whole surface only for a full-SDK or parity request; leave unresolved names explicitly `to-verify`.

## Required output

- release/commit/source snapshot;
- module/product inventory with confirmed versus `to-verify` status;
- lifecycle/API route map and migration traps;
- configuration/permission/privacy/release-channel inventory;
- upstream role/tool/sample handoff;
- build, mock, simulator, connected-device, and physical proof gates;
- unresolved “Gen 3,” audio, IMU, Web Apps, or regular-SDK questions.

## Hard boundaries

- Never treat `llms.txt`, MCP search, a repo sample, or a copied upstream skill
  as proof that the target package compiles or the glasses work.
- Never invent a module import from a broad platform index; verify package
  products and generated API symbols in the selected release.
- Never treat a phone AVAudioSession route as physical HFP glasses proof.
- Never map “Gen 3” to `.metaGlasses`, `.rayBanMeta`, or Display without current
  official mapping and named-device evidence.
- Never add credentials, release-channel values, raw media, or diagnostic
  payloads to the atlas or skill archive.
- Never conflate native DAT with the Web Apps DOM/hosted URL runtime.

## Related routes

- [Meta Wearables agentic team](../meta-wearables-agentic-team/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Full SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [DAT camera and audio](../meta-dat-camera-audio/SKILL.md)
- [DAT Display](../meta-dat-display/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Meta source refresh](../meta-wearables-source-refresh/SKILL.md)

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT iOS README](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta Wearables MCP](https://mcp.developer.meta.com/wearables)
- [Meta DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [Meta DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Meta DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
