# Version-dependency and device-compatibility evidence

Use this route whenever a feature names Gen 2, Gen 3, Meta Glasses, Ray-Ban
Display, a firmware number, or a DAT/Web Apps release. A retail label is not a
compatibility contract:

```text
consumer label != SDK/artifact revision != companion/firmware tuple != observed capability
```

This route prevents the team from promising support from a product announcement,
an enum value, or a successful registration alone. It is intentionally separate
from the broader [device-generation matrix](16-device-generation-and-runtime-support-matrix.md)
because version dependencies and firmware drift change independently of product
names.

Use the portable [compatibility evidence-packet template](../skills/packages/meta-wearables-device-compatibility/references/compatibility-evidence-packet.yaml)
for every named-device or generation handoff, then run:

```bash
python3 ../skills/packages/meta-wearables-device-compatibility/scripts/validate_compatibility_packet.py <packet.yaml>
```

The validator enforces the complete tuple, per-capability fallback, redaction,
all `COMP-*` evidence rows, and the boundary between a draft/physical-ready
packet and a completed compatibility claim.

## Current source snapshot

The public 0.9.0 repositories and changelogs were available on 2026-08-22:

| Source | Current signal | What it establishes | What remains open |
| --- | --- | --- | --- |
| [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) | 0.9.0 released 2026-08-03; consolidated `Camera`, Display `ButtonGroup`, listener aggregation, and updated release configuration | Versioned iOS migration facts | A named app's resolved package, target build, companion version, firmware, and physical behavior |
| [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md) | 0.9.0 released 2026-08-03; consolidated `Camera`, Display builder/input changes, Java-visible `DatResult`, DAM opt-out removal | Versioned Android migration facts | A named Gradle graph, target build, companion version, firmware, and physical behavior |
| [Android package registry](https://github.com/facebook/meta-wearables-dat-android/packages) | `mwdat-core`, `mwdat-camera`, and related artifacts publish 0.9.0 | Public artifact/version availability | Authorized GitHub Packages access and the resolved dependency graph |
| [Wearables version dependencies](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/) | Returns a login-gated page in this environment | The page exists and is an authenticated source gate | Exact current app/firmware compatibility values |
| [Full public reference](https://wearables.developer.meta.com/llms.txt?full=true) | Public v0.9 reference names hardware families, DAT, Web Apps, and version/dependency entry points | Discovery and source-map context | An exact target's support or a public Gen 3 mapping |
| [Public Gen 2 firmware report](https://github.com/facebook/meta-wearables-dat-ios/issues/265) | A closed issue reports a 0.9.0 session failure after Gen 2 firmware 126→127; it is a community observation, not a Meta compatibility guarantee | Why firmware drift must be tracked separately | Whether V127 is officially supported, unsupported, or fixed in a later release |

Do not turn the issue report into an official support statement. Treat it as a
refresh trigger and a reason to record the exact firmware in every device test.

## Compatibility status matrix

| Named target | Current public signal | Safe status | Required closure evidence |
| --- | --- | --- | --- |
| Ray-Ban Meta Gen 2 | Full reference and DAT model-family sources name Gen 1/Gen 2; exact version table is access-gated | `source` + `to-verify` | Exact retail/model identity, DAT artifact, Meta AI version, glasses firmware, compatibility state, and physical camera/audio run |
| Ray-Ban Meta Optics (Gen 2) | Public DAT model-family signal exists; retail capability is not inferred from styling | `source` + `to-verify` | Same tuple plus capability-specific result; do not inherit Display support |
| Meta Ray-Ban Display | Native DAT Display and separate Web Apps routes exist; support is capability/firmware-gated | `device-gated` | `supportsDisplay`/equivalent, Display or Web App launch, input, legibility, clear/exit, and recovery on the named pair |
| Meta Glasses | Product and SDK model-family wording exist, but this snapshot does not establish a “Gen 3” alias | `to-verify` | Official current mapping, runtime `DeviceType`, firmware, capability profile, and physical result |
| “Gen 3” | User/consumer label; no reviewed public DAT enum or support table maps it to a runtime identity | `to-verify` | Exact product identity plus official source and named-device evidence; never alias to `.metaGlasses`, `.rayBanMeta`, or Display |
| “Regular SDK” | Reviewed public journeys are native DAT and hosted Web Apps; no third public SDK family was established | `ambiguous` | Choose native DAT, native Display, Web Apps, or phone fallback before implementation |

## Compatibility tuple

Capture these fields before interpreting a failure or claiming support:

```yaml
consumer_label: "Ray-Ban Meta Gen 2"
retail_sku_or_product_name: "to-verify"
sdk_route: native-dat-ios | native-dat-android | native-dat-display | web-app | phone-fallback
sdk_package_or_artifact: "exact package/artifact"
sdk_version_and_commit: "0.9.0 / selected revision"
phone_os_and_build: "exact value"
companion_meta_ai_version: "exact value"
glasses_runtime_device_type: "observed value"
glasses_firmware: "exact value"
on_glasses_dat_app_version: "exact value or unknown"
link_and_transport: bluetooth | wifi | mixed | unknown
registration_permission_compatibility: "observed states"
capability_profile: "camera/audio/display/input/etc."
account_mode: developer-mode | release-channel | unknown
evidence_level: source | static | build | mock | browser-sim | connected | physical | release
observed_at: "UTC timestamp"
```

If any identity field is unknown, the result can diagnose an attempted state
but cannot establish universal device support.

## Decision and refresh workflow

1. Freeze the source URLs, retrieval date, repository tag/commit, selected iOS
   package or Android artifact, and Web App revision.
2. Resolve the consumer wording to an exact product/SKU; keep “Gen 3” and
   “regular SDK” unresolved until an official mapping exists.
3. Read the authenticated version-dependency page if available. If it is
   inaccessible, record `access-gated` and do not fill its values from memory,
   search snippets, or a community issue.
4. Inspect the actual target package/artifact and record the platform minimum,
   migration surface, configuration, and capability symbols.
5. Record the full compatibility tuple before pairing or reproducing a failure.
6. Test capabilities independently: registration, camera/photo, HFP/A2DP,
   native Display, Web App launch/input, update navigation, disconnect, doff/
   fold, thermal/power, and recovery.
7. Classify each result as `source`, `static`, `build`, `mock`, `browser-sim`,
   `connected`, `physical`, or `release`; never promote an adjacent evidence
   level.
8. Add a refresh trigger when firmware, Meta AI, on-glasses DAT app, SDK tag,
   release channel, or target OS changes.

## Evidence rows

| ID | Evidence level | Required record | Closure claim |
| --- | --- | --- | --- |
| `COMP-SOURCE-01` | `source`/`access-gated` | URLs, revisions, retrieval date, page access state, and first-party/community classification | The compatibility question was scoped to a known source snapshot |
| `COMP-STATIC-01` | `static` | Exact iOS package products or Android artifacts, target minimums, configuration, and model/capability symbols | The target can address the intended API surface |
| `COMP-VERSION-01` | `static`/`access-gated` | Authenticated version table result, or an explicit unavailable result | Version dependency values are known or honestly unresolved |
| `COMP-TUPLE-01` | `connected` | Device identity, firmware, Meta AI/on-glasses DAT versions, link, compatibility, permissions, and account mode | The named pair reached a connected/diagnosable state |
| `COMP-CAPABILITY-01` | `physical` | One named operation per capability with result, processing path, and recovery outcome | The named pair performed that capability on that build |
| `COMP-FIRMWARE-01` | `physical`/`source` | Before/after firmware, first failure, exact error, attempted recovery, and post-state | Firmware drift is isolated without asserting universal support |
| `COMP-GEN3-01` | `source`/`physical` | Official mapping, runtime identity, and repeated operation on the named target | A Gen 3 claim is justified, or remains `to-verify` |
| `COMP-RELEASE-01` | `release` | Signed artifact, channel/tester state, target tuple, and post-install operation | The selected compatibility claim survives the intended distribution path |

## Hard boundaries

- A version number, retail label, model enum, registration success, or
  `supportsDisplay()` result does not prove every capability on every firmware.
- A closed public issue is a troubleshooting signal, not an official support
  table or a reason to declare a firmware unsupported.
- A login-gated version table remains unknown until an authorized view is
  available; do not reconstruct it from snippets.
- “Gen 3” must remain `to-verify` unless current official mapping and named
  runtime evidence close it.
- MockDevice, browser simulation, compile success, and connected status do not
  close physical camera, audio, Display, input, thermal, or release evidence.
- Never store package tokens, client credentials, tester data, private project
  IDs, raw media, or diagnostic identifiers in this route or its skill archive.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android package registry](https://github.com/facebook/meta-wearables-dat-android/packages)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
- [Public Gen 2 firmware report](https://github.com/facebook/meta-wearables-dat-ios/issues/265)
- [Portable compatibility evidence-packet template](../skills/packages/meta-wearables-device-compatibility/references/compatibility-evidence-packet.yaml)
