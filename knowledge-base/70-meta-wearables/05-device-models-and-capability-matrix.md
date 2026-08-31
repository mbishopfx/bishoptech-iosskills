# Device models and capability matrix

Keep consumer product naming, SDK model identity, and runtime capability as
three separate fields. The current public DAT 0.9.0 changelog names these
`GlassesModel` values for mock-device construction:

```text
.rayBanMeta
.oakleyMetaHSTN
.oakleyMetaVanguard
.rayBanMetaOptics
.metaGlasses
```

Those enum cases are API identifiers, not a complete consumer catalog and not a
promise that every case supports every capability.

Use the [device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
for current product naming, the “Gen 3”/Meta Glasses ambiguity, Developer
Center access state, and the evidence protocol. This page remains the compact
SDK-model and capability reference.

The current full public DAT guide separately states support for Ray-Ban Meta
Gen 1 and Gen 2, Ray-Ban Meta Optics, and Meta Ray-Ban Display, with Meta AI app
and glasses-firmware version dependencies. Treat that product statement and
the SDK enum/runtime capability as separate facts.

## Working matrix

| Consumer wording | Current public SDK/route signal | Camera/stream | Display | Mapping status |
| --- | --- | ---: | ---: | --- |
| Ray-Ban Meta (Gen 2) | The consumer product name is official; the DAT mock enum is `.rayBanMeta`. | Runtime-check | Runtime-check | Treat `.rayBanMeta` as the current API family name, but verify the exact hardware/firmware mapping in the Developer Center and on the pair. |
| Ray-Ban Meta Optics (Gen 2) | `.rayBanMetaOptics` appears in the current mock enum. | Runtime-check | Runtime-check | API name is known; device capability and firmware remain gates. |
| Meta Ray-Ban Display | Display capability was added to DAT; use `supportsDisplay()` and the Display route. | Runtime-check | Expected display route | Verify the actual pair, firmware, DAT app, and link state. |
| Oakley Meta HSTN | `.oakleyMetaHSTN` appears in the current mock enum. | Runtime-check | Runtime-check | Do not infer Display support from the model name. |
| Oakley Meta Vanguard | `.oakleyMetaVanguard` appears in the current mock enum. | Runtime-check | Runtime-check | Do not infer Display support from the model name. |
| Meta Glasses | `.metaGlasses` appears in DAT 0.8+. | Runtime-check | Runtime-check | Use runtime metadata and current compatibility guidance. |
| “Gen 3” | No current official public DAT enum/product mapping was found in this refresh. | Unknown | Unknown | Keep as `to-verify`; do not silently alias to `.metaGlasses` or Display. |

The runtime route should surface `deviceType`, `supportsDisplay()` or the
equivalent current predicate, `linkState`, `compatibility`, and device health.
If compatibility reports a required firmware or DAT-on-glasses update, route
the person to the SDK's update action and keep the capability unavailable until
the update state changes.

## Capability contract

Before showing a glasses action, evaluate:

```text
known device identifier
  + current link state
  + registration state
  + permission state
  + compatibility state
  + capability predicate
  + session state
  + thermal/battery/power state
```

This prevents a UI label like “Display glasses” or “Gen 3” from becoming an
authorization shortcut. Store the observed metadata with a timestamp and
source revision when it affects a consequential decision.

## Device-proof matrix

| Claim | Minimum useful evidence |
| --- | --- |
| SDK recognizes a model enum | Source/SDK or MockDevice fixture. |
| Device is selected | Target/static plus a named test device or deterministic mock. |
| Camera works | Physical/system run on the named pair/build/firmware, or clearly labeled MockDevice evidence for logic only. |
| Display works | Physical/system Display Access task on a named display-capable pair. |
| Captouch/Neural Band interaction works | Physical/system task; browser arrow keys and MockDevice gestures are not equivalent proof. |
| Firmware/DAT app update recovery works | Physical/system run that triggers the compatibility state and completes the update handoff. |
| Public publishing works | Meta release-channel/project evidence and the exact distributed build; current preview eligibility remains a separate policy gate. |

## Sources

- [DAT iOS changelog and model enum](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS MockDevice testing skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [DAT iOS Display Access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT Android changelog and model enum](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [Full Wearables platform reference and version dependencies](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta Ray-Ban Meta (Gen 2) product announcement](https://about.fb.com/news/2026/05/ray-ban-meta-ai-glasses-launch-in-japan/)
- [Meta Glasses product announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/)
