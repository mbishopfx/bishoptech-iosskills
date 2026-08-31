# Operational readiness and recovery

This route turns a Meta Wearables integration from a source-level implementation
into an observable, recoverable system. A wearable feature spans the mobile
target, DAT artifact, Meta AI companion, glasses firmware, on-glasses DAT app,
account/project, transport, and release channel. A failure in any one layer can
look like a camera, Display, audio, or session bug.

Reviewed 2026-08-22 against the current public DAT iOS/Android changelogs and
the raw DAT-filtered reference. Re-open the version-dependencies and known-issues
pages for every named-device run; access-gated tables and issue reports are not
substitutes for a target observation.

## The operational tuple

Record these values before debugging or calling an integration ready:

| Layer | Required identity | Evidence boundary |
| --- | --- | --- |
| Mobile target | iOS/Android, target, OS, app version/build, signing mode | Static/build/signed |
| DAT artifact | SPM tag/commit or Maven coordinates/version | Source/package/compile |
| Companion | Meta AI installed/version/foreground state | Connected observation |
| Glasses | consumer label, runtime `DeviceType`, firmware, capability response | Connected/physical |
| On-glasses app | DAT app present, update-required state, post-update result | Physical/system |
| Account/project | Developer Mode or release channel, project, tester/configuration state | Access-gated/signed |
| Transport | Bluetooth, Wi-Fi/local network, Internet, link state | Connected/physical |
| Requested operation | registration, session, camera, HFP/A2DP, Display, update, recovery | Scripted evidence |

Do not fill a missing field with a neighboring generation, a stale sample, or a
consumer product nickname. Use `unknown`, `access-gated`, `source-conflict`, or
`to-verify` instead.

## Current source signals and conflicts

The raw public DAT reference currently states that Display development requires
Meta AI 272 or later, firmware 125 or later, the glasses worn during setup, and
Developer Mode. It also documents that distributed builds use release channels
and application identifiers, while Developer Mode has different registration
behavior. These are source-level prerequisites, not evidence that a particular
pair has the required on-glasses DAT app or that a release-channel assignment
was provisioned successfully.

The public 0.9.0 changelogs add operationally important signals:

- iOS raises the minimum deployment target to 17.2; Android exposes the
  consolidated camera lifecycle, Java-visible `DatResult`, Display tap/click,
  local `Bitmap` images, and crash-reporting opt-out.
- DAM opt-out configuration is obsolete in 0.9.0; stale examples that add the
  old key must remain a migration trap, not copied setup.
- iOS and Android expose explicit session/camera/display stop and terminal
  states. Do not restart during a thermal, battery, peak-power, doff, or unknown
  protocol failure without recording the first terminal signal.
- The SDK exposes documented navigation for firmware and on-glasses DAT-app
  updates in the source history. An update route being callable does not prove
  the update was delivered or that the original operation recovered.

The version-dependencies page is the authority for the selected account and
target. If its current table differs from the raw reference, record both values
as a `version-conflict` and use the named target’s observed compatibility result.
Public GitHub issues/discussions can reveal recurring provisioning or protocol
failures, but they are troubleshooting signals—not official support guarantees.

## Developer Mode and release channels

| Mode | Establishes | Does not establish |
| --- | --- | --- |
| Developer Mode | local registration and debug integration for the named target | release authorization, attestation, signed distribution, store approval, or production |
| MockDevice/browser | deterministic app state, layout, and recovery logic | firmware, radio, optics, HFP, thermal timing, or physical input |
| Connected physical device | the named pair completed the scripted operation | other models, future generations, or release readiness |
| Signed release channel | tester/account/configuration and named build path | Store approval or production behavior |
| Production | deployed behavior under its actual distribution | untested models, firmware, or broader capability claims |

For a release-channel run, verify the exact application ID, callback, package or
bundle identity, signing/app-attestation values, tester invitation, channel
selection, and installed build. Keep secrets in local secure configuration and
report only redacted identifiers or hashes.

## Recovery state machine

1. **Preflight:** compare the full tuple to the current source and label every
   value `source`, `static`, `observed`, `access-gated`, `conflict`, or `unknown`.
2. **Register:** verify companion presence, account/mode, callback, permissions,
   and network. Record the first registration error, not only the final UI.
3. **Select:** observe the runtime device identifier, model, link state,
   compatibility, and capability predicate. Never substitute another pair.
4. **Start:** observe session and capability state; preserve terminal `.stopped`
   and typed errors. Do not treat a timeout or no-eligible-device result as a
   generic retry invitation.
5. **Operate:** bound camera/audio/display work, honor doff/fold/disconnect and
   display sleep, and stop resources at the documented lifecycle boundary.
6. **Recover:** apply one documented, least-invasive action—permission reset,
   companion update, firmware route, DAT-app route, re-pair, or channel fix—then
   record the post-action state under a new run ID.
7. **Close:** mark `recovery-attempted` or `recovery-observed`; only the latter
   may support a recovery claim. A repeated unknown protocol error stays
   `to-verify` and should be escalated with a redacted packet.

## Failure-class contract

| Signal | Owner | Required behavior |
| --- | --- | --- |
| Missing config/package/permission | app/static | fix and rebuild; preserve old run identity |
| Release registration blocked | account/channel | verify project, app identity, signature, tester, and channel |
| Companion absent or callback fails | Meta AI/app integration | install/update companion and verify URL handling |
| Firmware/compatibility update required | firmware/device | use the documented update flow and observe the post-update version |
| DAT app on glasses update required | on-glasses provisioning | use the documented route; do not loop failed installs |
| No eligible device/link unavailable | transport/selection | inspect power, wear/fold, Bluetooth/Wi-Fi/Internet, selector, and permissions |
| Doff/hinges/disconnect | lifecycle | pause/stop according to the capability contract; release at terminal stop |
| Thermal/battery/peak power | safety | stop workload, surface status, cool/charge, and require deliberate restart |
| Unknown protocol or version mismatch | source/runtime conflict | preserve tuple and redacted diagnostics; stop at `to-verify` |

## Evidence tasks

Use the [device and release evidence packet](12-device-and-release-evidence-packet.md)
and the portable [operational-readiness skill](../skills/packages/meta-wearables-operational-readiness/SKILL.md).

| ID | Task | Evidence level |
| --- | --- | --- |
| `OPS-SOURCE-01` | Re-open changelogs, raw reference, version dependencies, known issues, and release guidance; record revision/date. | `source`/`access-gated` |
| `OPS-CONFIG-01` | Validate target package/artifact, deployment/min SDK, callback, permissions, privacy, and mode-specific configuration without exposing secrets. | `static` |
| `OPS-PAIR-01` | Record companion, account/mode, runtime model, firmware, on-glasses DAT-app state, link, and capability metadata for a named pair. | `connected`/`physical` |
| `OPS-RECOVERY-01` | Execute one scripted failure/recovery path and record first error, action, post-state, and whether the original operation completed. | `physical`/`system` |
| `OPS-THERMAL-01` | Observe thermal/battery/peak-power/stop behavior for the actual camera/audio/display workload. | `physical` |
| `OPS-CHANNEL-01` | Install and exercise the exact signed build through the named release channel with the tester account and firmware tuple. | `signed`/`release-channel` |

No source, mock, compile, or Developer Mode result closes `OPS-RECOVERY-01`,
`OPS-THERMAL-01`, or `OPS-CHANNEL-01`.

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT-filtered full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Wearables known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Wearables release-channel guidance](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [On-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
