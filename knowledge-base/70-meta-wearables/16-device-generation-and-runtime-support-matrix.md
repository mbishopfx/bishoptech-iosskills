# Device-generation and runtime-support matrix

Use this page before selecting a target or promising support for “Gen 2,”
“Gen 3,” Ray-Ban Display, Meta Glasses, Oakley Meta, or “regular SDK.” It
keeps three different facts separate:

```text
consumer product label != SDK model identity != observed capability profile
```

The page is a compatibility and evidence route, not a consumer product
catalog. It was refreshed 2026-08-22 against the DAT repositories, their
versioned changelogs, current official Meta product announcements, and the
Developer Center access result available in this environment.

## What the current public sources establish

| Layer | Current evidence | Evidence level | Cannot prove |
| --- | --- | --- | --- |
| Consumer naming | Meta publicly names Ray-Ban Meta (Gen 2), Ray-Ban Meta Optics (Gen 2), Oakley Meta products, and a separate Meta Glasses line. | `source` | DAT artifact support, a specific `DeviceType`, Display capability, or a particular firmware build. |
| Native SDK identity | DAT 0.8+/0.9 source and MockDevice routes expose model-family identifiers such as `.rayBanMeta`, `.rayBanMetaOptics`, `.oakleyMetaHSTN`, `.oakleyMetaVanguard`, and `.metaGlasses`. | `source`/`SDK` candidate | A one-to-one mapping from an enum case to every retail SKU, generation, firmware, or capability. |
| Native Display | DAT Display is capability-gated; use the current runtime predicate and Display session route. | `source`/`to-verify` | A product name or frame style being Display-capable. |
| Display Web Apps | Web Apps are a separate hosted route for the Ray-Ban Display surface with their own viewport, input, deployment, and physical-proof contract. | `source`/`browser-sim` | Native DAT camera/audio access, a Web App release channel, or physical delivery from a browser simulator. |
| Full DAT reference | The raw `llms.txt?full=true&product=dat` endpoint identifies DAT v0.9, Gen 1/Gen 2/Optics/Display hardware, HFP audio, and the broader conceptual index. | `source` | Exact version-dependency values, importable package symbols, and target compile/runtime behavior. |
| Developer Center UI | The interactive development page is rendered as a login-gated HTML surface here, while the raw full-reference endpoints remain readable. | `source` + `access-gated` | Hidden authenticated tables, exact version-dependency values, and target compile/runtime behavior. |

## Product label to SDK route

| Product wording | Public SDK signal | Default route | Status and required treatment |
| --- | --- | --- | --- |
| Ray-Ban Meta (Gen 2) | The v0.9 full reference explicitly lists Ray-Ban Meta Gen 1 and Gen 2 support; `.rayBanMeta` is also a model-family signal in the DAT mock/API surface. | Native DAT for camera/photo/session work; phone fallback for unsupported capability. | `source` + `to-verify`; record actual runtime identity, firmware, compatibility, and capability response. Do not generalize one Gen 2 SKU to every other model. |
| Ray-Ban Meta Optics (Gen 2) | `.rayBanMetaOptics` appears in the DAT model-family surface. | Native DAT with the same runtime gates as other displayless candidates. | `source` + `to-verify`; optical styling does not establish camera, audio, or Display behavior. |
| Meta Glasses (2026 product line) | [Meta’s official announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/) names a separate Meta Glasses line; the current v0.9 DAT hardware list names Gen 1, Gen 2, Optics, and Display but does not list Meta Glasses. DAT history includes `.metaGlasses` as a model-family signal. | Do not choose a route from the product announcement or enum alone. Start with full-SDK audit and runtime metadata. | `source` product label + `to-verify` runtime mapping; Meta’s official article does not call this line “Gen 3,” and this source set does not authorize that alias. |
| Meta Ray-Ban Display | Product/display naming plus DAT `supportsDisplay()`/equivalent and the separate Web Apps route. | Native `MWDATDisplay`/`mwdat-display` or hosted Web App. | `device-gated`; verify Display capability, firmware, link, input hardware, and physical legibility. “Display” is not a generation number. |
| Oakley Meta HSTN/Vanguard | DAT model-family identifiers and official product announcements exist. | Native DAT only where the selected artifact and runtime capability support the requested operation. | `source` + `to-verify`; do not infer Ray-Ban Display behavior from an Oakley product name. |
| “Regular Gen 3” | No current official public DAT enum or support table in the reviewed sources uses this exact label; Meta’s official 2026 announcement uses “Meta Glasses,” not “Gen 3,” and the v0.9 hardware list does not list that product name. | Full-SDK audit, then phone/mock fallback until identity is resolved. | `to-verify`; require the exact retail/product name, runtime model identity, firmware, companion version, selected artifact, and named-device evidence. |
| “Regular SDK” | The reviewed public native lane is named DAT; Web Apps are a separate hosted lane. | Clarify native DAT versus Web Apps before implementation. | `ambiguous`; do not invent a third public SDK family. |

The product announcements are useful for naming and launch context only. The
DAT changelogs and selected package/API reference own symbols and migration
behavior; a physical target owns the final capability claim.

## Runtime support contract

Represent a target as a profile rather than a Boolean such as `isGen3`:

```text
consumerLabel
sdkDeviceType
platformAndArtifactRevision
phoneOSAndCompanionVersion
glassesFirmwareAndDATVersion
linkState
registrationAndPermissionState
compatibilityState
capabilityPredicates
accountOrReleaseChannel
evidenceLevel
observedAt
```

Every capability decision should then be evaluated independently:

| Requested capability | Required decision | Safe fallback |
| --- | --- | --- |
| Camera/photo | Does the selected target expose the current camera route, permission, session, thermal/battery state, and compatible firmware? | Phone camera or explicit unavailable state. |
| Audio | Does the full DAT reference’s HFP/A2DP route resolve in the selected artifact and target, and is the input/output actually glasses audio rather than a phone microphone or A2DP-only playback? | Phone audio, typed unavailable state, or user-selected recording source. |
| Native Display | Does the runtime report Display support and can the named pair render/input/clear/recover? | Phone UI or audio-first result. |
| Web App | Is the public HTTPS app added/launched on the named Display target, and do each of the source-conflicted features pass independently? | Phone companion flow or a smaller confirmed Web App surface. |
| “Gen 3” support | Does an official source and runtime identity establish the mapping? | Keep `to-verify`; never alias to `.metaGlasses`, `.rayBanMeta`, or Display. |

## Evidence protocol

Run these rows in the [device and release evidence packet](12-device-and-release-evidence-packet.md):

| Task ID | Evidence | Operation | Claim it supports |
| --- | --- | --- | --- |
| `GEN-SRC-01` | `source` | Freeze the official product label, DAT revision, changelog, Developer Center access state, and Web Apps revision. | The compatibility question was scoped to a known source snapshot. |
| `GEN-STATIC-01` | `static`/`build` | Inspect the actual iOS package products or Android Gradle artifacts and record the model/capability symbols used by the target. | The target can address the selected API surface; not hardware support. |
| `GEN-CONNECTED-01` | `connected` | Pair the named device, record runtime identity, firmware, companion version, link, permission, compatibility, and capability state. | The selected target was recognized and connected. |
| `GEN-PHYSICAL-01` | `physical` | Exercise the requested camera/audio/Display/input operation plus disconnect, denial, doff/fold, and recovery cases. | The exact named pair/build performed the scripted operation. |
| `GEN-CROSS-01` | `physical` per target | Repeat the same script on Gen 2 and the alleged Gen 3 target without substituting labels. | Only the named target/build pair; never universal generation support. |

No source, compile, MockDevice, browser-simulator, or connected result closes
`GEN-PHYSICAL-01`. No product announcement closes `GEN-STATIC-01` or proves a
third-party DAT capability.

The current full-reference v0.9 text is stronger than a product announcement
for the listed Gen 1/Gen 2/Optics/Display support, but its relative Version
Dependencies route still needs to be checked for the exact Meta AI app and
glasses-firmware pair. The raw endpoint is therefore `source`, not universal
hardware proof.

## Refresh triggers

Refresh this page and the full-SDK audit when any of the following changes:

- a DAT tag/changelog adds or renames a model-family identifier;
- the authenticated Developer Center exposes a new compatibility or hardware
  support table;
- Meta or EssilorLuxottica introduces a product marketed as a generation or a
  Display variant;
- a named target reports a new `DeviceType`, firmware/DAT version, capability,
  or compatibility state;
- the Android artifact, iOS package, Web Apps toolkit, or Web Apps runtime
  changes its support contract.

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Ray-Ban Meta (Gen 2) announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/)
- [Ray-Ban Meta Gen 2 and Optics announcement](https://about.fb.com/news/2026/03/meta-ai-glasses-built-for-prescriptions/)
- [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
- [Meta Ray-Ban Display announcement](https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT-filtered full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
