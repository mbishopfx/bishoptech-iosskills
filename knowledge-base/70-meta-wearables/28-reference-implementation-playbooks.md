# Meta Wearables reference implementation playbooks

This route turns the source/API inventory into repeatable implementation
handoffs for the most common product shapes: native Display, camera-to-phone
processing, audio-first Gen 2 fallback, Ray-Ban Display Web Apps, and one
shared outcome across iOS, Android, native Display, and Web Apps.

The detailed portable playbooks live in the [application-architecture package](../skills/packages/meta-wearables-app-architecture/references/vertical-slice-playbooks.md).
Load the [source-pinned API register](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
first and filter the exact `IOS-*`, `AND-*`, `WEB-*`, compatibility, and
evidence rows. A playbook is an implementation plan, not proof that a symbol
compiles or that a named pair of glasses works.

## Slice catalog

| Playbook | Primary route | Best use | Required proof boundary |
| --- | --- | --- | --- |
| A — Native Display glance card | Native DAT iOS/Android + native Display | Compact result with one or two physical actions | Runtime Display capability, target build, named physical Display/input run |
| B — Camera/photo to phone-local result | Native DAT camera + phone processing | Preview/photo followed by bounded local work | Camera/photo tuple, privacy/retention, physical camera result if claimed |
| C — Audio-first path | A2DP/HFP or phone fallback | Non-Display or uncertain-generation experience | Active audio route, consent, physical audio result, typed fallback |
| D — Ray-Ban Display Web App | Hosted Web Apps | HTML/CSS/JavaScript on Meta Ray-Ban Display | HTTPS add/launch, browser simulation, named physical MRBD run, release revision |
| E — Shared outcome | Separate adapters + shared domain policy | One product across iOS/Android/Web/phone | Per-surface evidence; no symbol or capability flattening |

## Common implementation contract

Before creating files, freeze:

- one user outcome and one primary surface;
- the phone fallback and the highest-consequence failure;
- exact app target, OS/min SDK, DAT package/artifact or Web App revision;
- runtime model, firmware, Meta AI/on-glasses DAT-app state, and release mode
  when known;
- API row IDs, processing location per data type, retention/deletion, owner,
  session epoch, stop path, and proof level.

The playbooks enforce the same hard boundaries as the rest of the lane:

- Native DAT, native Display, Web Apps, and phone fallback are separate
  adapters.
- A Gen 2/Gen 3 label never substitutes for a runtime tuple or capability
  predicate; Gen 3 remains `to-verify` in the current public snapshot.
- Phone-local processing is not glasses-native processing.
- MockDevice/browser simulation proves deterministic logic or layout only.
- A source row or package name is not compile, physical, signed, or production
  proof.
- Raw frames, audio, transcripts, device identifiers, tokens, and private
  project data stay out of fixtures, logs, and handoff packets.

## Team handoff

Use the detailed [vertical-slice playbooks reference](../skills/packages/meta-wearables-app-architecture/references/vertical-slice-playbooks.md)
for the state machine, adapter map, resource ownership, data path, fallback,
and proof ladder. Return:

```text
playbook: A | B | C | D | E
outcome: <one sentence>
primary_surface: <native DAT / Display / Web App / phone>
fallback_surface: <route>
target_tuple: <app/OS/artifact/runtime/phone/companion/firmware/channel>
api_rows: <manifest and evidence IDs>
data_path: <glasses-native / phone-local / remote / mixed / unknown>
state_owner: <coordinator and capability owner>
proof_completed: <exact evidence level and task>
open_gates: <source/build/account/device/privacy/release gaps>
```

## Sources

- [Portable vertical-slice playbooks](../skills/packages/meta-wearables-app-architecture/references/vertical-slice-playbooks.md)
- [Application architecture and platform boundaries](19-application-architecture-and-platform-boundaries.md)
- [Source-pinned API surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [On-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
