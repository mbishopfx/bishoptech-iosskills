# Meta Wearables compatibility contract

Use this contract as the compact fixture for device/version decisions. It is
not a support table; it tells the agent what must be known before one can be
written.

## Input record

```yaml
label: "Ray-Ban Meta Gen 2"
route: native-dat-ios
package_or_artifact: "exact value"
sdk_revision: "exact tag/commit"
phone_os_build: "exact value"
meta_ai_version: "exact value"
device_type_observed: "exact value or unknown"
firmware: "exact value or unknown"
on_glasses_dat_app: "exact value or unknown"
link: bluetooth | wifi | mixed | unknown
permission_and_compatibility: "observed state"
account_mode: developer-mode | release-channel | unknown
evidence_level: source | static | build | mock | browser-sim | connected | physical | release
```

## Status rules

| Status | Meaning | Next action |
| --- | --- | --- |
| `current` | The selected source/package and target evidence agree for the stated scope | Preserve the tuple and date; do not generalize beyond it |
| `to-verify` | A required mapping, version value, symbol, or target result is missing | Name the exact source, build, or physical task |
| `access-gated` | The authoritative page exists but requires an authorized login | Request/access the page; do not reconstruct the values |
| `device-gated` | The API path is known but hardware/firmware capability is not proven | Run the named operation on the named pair |
| `source-conflict` | First-party sources disagree | Preserve both revisions and use the selected artifact/runtime as the next gate |
| `unsupported` | The selected source or target explicitly excludes the capability | Keep a typed fallback and record the source |

## Minimum evidence mapping

| Claim | Minimum evidence | Insufficient evidence |
| --- | --- | --- |
| SDK package/artifact can address the route | `COMP-STATIC-01` | Product announcement or role prose |
| Version pair is documented | `COMP-VERSION-01` | Search snippet or remembered table |
| Named glasses are recognized | `COMP-TUPLE-01` | Registration alone or retail label |
| Camera/audio/Display/input works | `COMP-CAPABILITY-01` | Mock, browser simulator, or connected status |
| Firmware drift is causal | `COMP-FIRMWARE-01` | A single error without before/after tuple |
| Gen 3 is supported | `COMP-GEN3-01` | `.metaGlasses` enum or product naming |
| Release compatibility holds | `COMP-RELEASE-01` | Local debug build or channel creation |

## Redaction

Keep credentials and private identifiers as presence/status fields only:

```text
client_token: present-redacted
application_id: present-redacted
package_token: present-redacted
tester_or_project_id: present-redacted
raw_device_identifier: omitted
```

Never put these values in Markdown fixtures, a `.skill` archive, logs, or
diagnostic handoffs.

## Machine-checked evidence packet

Start from the [compatibility evidence-packet template](compatibility-evidence-packet.yaml)
and validate the completed or draft handoff:

```bash
python3 scripts/validate_compatibility_packet.py <packet.yaml>
```

The validator requires the source snapshot, complete target tuple, processing
claim, capability fallbacks, all eight `COMP-*` rows, open gates, next proof
task, and redaction record. It rejects sensitive values, duplicate or unknown
evidence IDs, unsupported route/status values, and a `completed` packet that
does not have connected tuple, physical capability, and release evidence. A
packet that mentions Gen 3 must retain `COMP-GEN3-01`; `to-verify` is valid for
an unresolved draft, while completion requires official mapping plus named
physical/release evidence.

## Sources

- [Version-dependency evidence route](../../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md)
- [Device-generation matrix](../../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [Evidence packet](../../../../70-meta-wearables/12-device-and-release-evidence-packet.md)
- [Compatibility evidence-packet template](compatibility-evidence-packet.yaml)
