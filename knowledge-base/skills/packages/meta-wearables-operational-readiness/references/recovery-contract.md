# Operational recovery contract

Use this reference as a compact runbook. It is a decision contract, not a
promise that Meta can repair a backend, firmware, or on-glasses DAT-app issue
from the mobile app.

## Run identity

| Field | Record | Evidence label |
| --- | --- | --- |
| Run ID | Stable redacted identifier and timestamp | `observed` |
| Platform/target | iOS or Android, target name, app version/build | `static`/`observed` |
| DAT artifact | SPM tag/commit or Maven coordinates/version | `static` |
| Phone/companion | Phone OS, Meta AI version, companion installed/foreground state | `observed` |
| Glasses | Consumer label, runtime `DeviceType`, firmware, on-glasses DAT-app state | `observed`/`to-verify` |
| Account/channel | Developer Mode or release channel, project/tester state | `observed`/`access-gated` |
| Operation | Registration, session, camera, audio, Display, update, or recovery step | `observed` |
| Data path | Glasses-native, phone-local, remote, mixed, or unknown | compliance contract |

## Mode and gate matrix

| Mode | What it can establish | What it cannot establish |
| --- | --- | --- |
| Source/reference | documented API and stated prerequisites | package availability, account access, hardware behavior |
| Developer Mode | local registration path and debug integration | release authorization, app attestation, signed release, public distribution |
| MockDevice/browser simulator | deterministic state/layout/recovery logic | radio, firmware, optics, HFP, thermal timing, real input, physical display |
| Connected physical device | named pair completed the observed operation | other models, future generations, release readiness |
| Signed release channel | tester/account/configuration path for the named build and channel | Store approval or production behavior |
| Production | deployed route under its actual distribution | untested versions/models or broader product claims |

## Preflight tuple

Before starting a session, resolve these fields independently:

1. SDK package/artifact and repository revision.
2. Phone OS and target deployment/min SDK.
3. Meta AI companion version and installed state.
4. Glasses firmware and runtime model/capability metadata.
5. On-glasses DAT app presence/version/update-required state.
6. Account, project, application ID, callback, signature, token/configuration,
   and release-channel/tester state. Keep secrets in local secure config.
7. Bluetooth/Wi-Fi/local-network/Internet and permission state.
8. Requested capability and evidence level.

If one field is inaccessible, label it `access-gated` or `unknown`; do not
substitute the nearest public version or consumer product label.

## Failure classification and recovery

| First failing signal | Classify as | Safe next action |
| --- | --- | --- |
| Missing package/config/permission | target/config | Fix static files, reset permission deliberately, rebuild; capture the new build identity. |
| Registration blocked outside Developer Mode | account/channel | Verify project, application ID, signature, tester invitation, and channel; do not claim a device defect. |
| Meta AI absent/outdated or callback cannot open | companion | Install/update companion, verify URL scheme and callback, then re-run registration. |
| Firmware or compatibility reports update required | firmware | Open the documented firmware route, wait for the post-update state, re-pair only if instructed, and record firmware again. |
| DAT app on glasses update required | on-glasses provisioning | Use the documented DAT-app update route; if installation fails, preserve the exact error and escalate rather than looping. |
| No eligible device/link unavailable | transport/selection | Verify power, wear/fold state, Bluetooth/Wi-Fi/Internet, selector filter, and permissions; do not map another model as equivalent. |
| Permission denied/unavailable | consent/privacy | Explain purpose, request once, support denial and phone fallback, and retain no raw data by default. |
| Doff/hinges closed/disconnect | lifecycle | Stop or pause the capability according to its state contract; release resources only at terminal stop and allow deliberate restart. |
| Thermal/battery/peak-power signal | safety | Stop the workload, surface a human-readable status, cool/charge as appropriate, and never retry automatically. |
| Unknown protocol/error after matching setup | source/runtime conflict | Record SDK, companion, firmware, event trace, and redacted diagnostics; compare current known issues and stop at `to-verify`. |

## Recovery evidence

For each attempted recovery, record:

- pre-action state and exact first error;
- documented action taken and who/what initiated it;
- post-action companion, firmware, DAT-app, link, registration, and session state;
- whether the original operation completed;
- artifact/build and physical device identity;
- evidence level and remaining uncertainty.

The packet must distinguish `recovery-attempted` from `recovery-observed`.

## Redaction contract

Keep only hashes or stable redacted aliases for application IDs, signatures,
tokens, emails, serials, URLs containing credentials, raw frames, audio,
transcripts, and diagnostic bundles. Store full private artifacts outside the
knowledge base and record only their type, timestamp, checksum, and retention
owner.
