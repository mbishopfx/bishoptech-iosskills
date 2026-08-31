---
name: meta-wearables-device-compatibility
description: Resolve Meta Wearables product labels, DAT iOS/Android versions, Web Apps revisions, glasses firmware, Meta AI companion versions, and capability support without inventing Gen 3 or “regular SDK” mappings. Use for Gen 2/Gen 3 support, firmware drift, version-dependency tables, device compatibility failures, release upgrades, cross-platform matrices, or any claim that a named Ray-Ban/Meta wearable is supported.
---

# Meta Wearables device compatibility

Resolve compatibility as a versioned, observed tuple rather than a Boolean
product label. This role owns the evidence needed to decide whether a named
DAT iOS, DAT Android, native Display, Web App, or phone-fallback route is safe
for a particular product, firmware, companion version, and release channel.

## Read before acting

- Read [version-dependency and device-compatibility evidence](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md)
  and its [compatibility contract](references/compatibility-contract.md).
- Use the [compatibility evidence-packet template](references/compatibility-evidence-packet.yaml)
  and run `python3 scripts/validate_compatibility_packet.py <packet>` before
  treating a compatibility handoff as ready for implementation or physical
  testing.
- Read the [device-generation and runtime-support matrix](../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
  before interpreting Gen 2, Meta Glasses, Display, or Gen 3 wording.
- Read the [full SDK capability matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
  before calling a route “full” or translating capability parity across Swift,
  Kotlin, and Web Apps.
- Read the [operational readiness route](../../../70-meta-wearables/18-operational-readiness-and-recovery.md)
  for companion, firmware, on-glasses DAT-app, transport, thermal/power,
  update, and recovery evidence.
- Read the [security/attestation route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
  for account mode, release channel, callback, identity, and credential gates.
- Read the [device-proof route](../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
  before promoting source, mock, browser, connected, or build results to
  physical or release claims.
- Refresh the official [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md),
  [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md),
  [version-dependencies page](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/),
  [full reference](https://wearables.developer.meta.com/llms.txt?full=true), and
  [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp).

## Compatibility workflow

1. Freeze exact platform, route, package/artifact and Web App revision, source
   URLs, retrieval date, and intended evidence level.
2. Resolve the retail name to a product/SKU and observed runtime identity.
   Keep “Gen 3” unresolved unless a current official mapping exists.
3. Read the authenticated version-dependency table. If it is inaccessible,
   record `access-gated`; never fill values from memory or community reports.
4. Inspect the actual target configuration and artifact/package symbols. Treat
   0.8→0.9 migration notes as compile gates, not optional prose.
5. Record the complete tuple: phone OS/build, Meta AI version, glasses firmware,
   on-glasses DAT-app version, link/transport, registration/permission/
   compatibility state, account mode, and observed `DeviceType`.
6. Exercise requested capabilities independently, including a negative path
   and recovery path. For Web Apps, separate simulator, hosted URL, add/launch,
   and physical Display results.
7. Classify each result with its actual evidence level and produce a fallback
   for every unresolved or unsupported capability.
8. Add a refresh trigger for firmware, companion, DAT app, OS, artifact, Web App
   runtime, release channel, or product-label changes.
9. Validate the sanitized packet. A `completed` packet requires connected tuple,
   physical capability, and release evidence rows; a Gen 3 packet cannot close
   without `COMP-GEN3-01` physical/release evidence.

## Fast path

Normalize one tuple—product label, runtime `DeviceType`, firmware, companion/DAT app, SDK artifact, target, and capability response—and mark every field observed, inferred, or `to-verify`. Resolve the requested capability only after the tuple is usable; never start implementation from a marketing label.

## Required output

- exact source and package/artifact snapshot;
- product-label → SDK route → runtime identity matrix;
- version-dependency access state and values only when directly observed;
- complete compatibility tuple;
- capability-by-capability status (`current`, `to-verify`, `device-gated`,
  `source-conflict`, `unsupported`, or fallback);
- migration implications for the selected DAT 0.9 target;
- first failure, bounded recovery, and post-action state for drift/failure;
- evidence rows `COMP-SOURCE-01` through `COMP-RELEASE-01`;
- explicit Gen 2 treatment and Gen 3 status;
- unresolved gaps and next refresh trigger.
- validator receipt from `validate_compatibility_packet.py`;

## Hard boundaries

- Do not map Gen 3 to `.metaGlasses`, `.rayBanMeta`, Display, or any enum from a
  product announcement.
- Do not call a consumer label, `DeviceType`, version number, or registration
  success proof of camera, audio, Display, input, thermal, or release support.
- Do not treat a public issue as first-party compatibility policy.
- Do not treat a login-gated page as known; record the access gap.
- Do not equate DAT iOS, DAT Android, and Web Apps symbols by naming similarity.
- Do not place credentials, package tokens, tester data, raw media, private
  project IDs, or unredacted device diagnostics in outputs or archives.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Full SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android package registry](https://github.com/facebook/meta-wearables-dat-android/packages)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
