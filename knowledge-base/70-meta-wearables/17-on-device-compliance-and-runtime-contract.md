# On-device compliance and runtime contract

This page defines “on-device compliant” as an observable data, capability, and
failure contract. It does not mean that a phone companion, Meta AI, or remote
service disappears from the product. Every feature must state where data is
captured, processed, transmitted, stored, and stopped.

## Processing boundary

Use explicit labels rather than a Boolean `onDevice`:

| Label | Meaning | Safe wording |
| --- | --- | --- |
| `glasses-native` | The named glasses perform the operation and the selected SDK/runtime exposes it. | “Runs on the glasses” only with target evidence. |
| `phone-local` | The phone companion performs the operation after receiving an allowed input. | “Processed locally on the phone,” not glasses-native. |
| `remote` | A network/vendor service is required. | Name the service and disclose the dependency. |
| `mixed` | The path crosses glasses, phone, and/or remote processing. | Describe each boundary. |
| `unknown` | The implementation or evidence does not establish the path. | Keep the claim `to-verify`. |

`on-device confirmed` requires the exact implementation path plus matching
static/connected/physical evidence. `local-first` is valid when local behavior
is the default and a remote fallback is explicit, bounded, and disclosed.

## Required runtime contract

Every target profile should record:

```text
consumerLabel != sdkDeviceType != observedCapabilityProfile
processingLocation
networkPolicy
permissionAndConsentState
linkAndCompatibilityState
thermalAndBatteryState
sessionAndLifecycleState
storageAndRetentionPolicy
fallbackAndRecoveryState
evidenceLevel
```

The [full-SDK matrix](15-full-sdk-capability-and-source-conflict-matrix.md)
owns the native module/artifact inventory. The [generation matrix](16-device-generation-and-runtime-support-matrix.md)
owns product-label versus runtime identity. This page owns the compliance claim
crossing those routes.

## Route guardrails

| Route | Minimum contract before implementation | Non-compliant shortcut |
| --- | --- | --- |
| iOS DAT camera/audio | Pinned package, iOS deployment target, permission copy, session/camera/audio ownership, bounded processing, stop/doff/thermal fallback | Calling phone microphone or a remote transcript glasses-native. |
| Android DAT camera/audio | Pinned `mwdat-*` artifacts, Manifest/runtime permissions, `DatResult`/`Flow` lifecycle, camera/audio route, R8/release configuration, fallback | Treating Kotlin examples as Swift parity or using old DAM/session metadata. |
| Native Display | Runtime display predicate, started session, compact content/input/error reducer, clear/stop, physical legibility and recovery | Rendering a mock or phone UI and calling it glasses delivery. |
| Display Web App | HTTPS, MRBD marker, 600×600 additive layout, focus/input/loading/error/exit states, public-data boundary, independent feature gates | Treating browser simulator, localhost, or toolkit prose as physical support. |

## Compliance review sequence

1. Freeze target, artifact, model, firmware, companion, account/channel, and
   requested capability.
2. Build the data-flow table for camera, audio, sensor, Display, diagnostics,
   identifiers, storage, and remote services.
3. Confirm permissions and notice happen before collection; make denial,
   disconnect, background, doff/fold, thermal, battery, and offline behavior
   user-visible and recoverable.
4. Bound memory, frame/audio queues, logging, cache, retention, and network
   destinations. Stop raw capture when the user leaves the active operation.
5. Apply the selected platform’s actual package/configuration and test static
   and deterministic fixtures before hardware.
6. Run the named connected/physical script for each hardware claim. Record
   exact device identity, firmware, companion, build, operation, and result.
7. Return claim status and fallback. Keep source-conflict and `to-verify` rows
   open until the evidence level actually required by the claim is present.

## Evidence tasks

| Task | Evidence | Purpose |
| --- | --- | --- |
| `ODC-SOURCE-01` | `source` | Freeze the current DAT/Web Apps source, policy, product, and version snapshot. |
| `ODC-STATIC-01` | `static`/`build` | Inspect package/artifact, permissions, privacy metadata, network, storage, and model/runtime symbols. |
| `ODC-MOCK-01` | `mock`/`browser-sim` | Exercise denial, disconnect, stale state, stop, fallback, loading, error, focus, and cache behavior deterministically. |
| `ODC-PHYS-01` | `connected`/`physical` | Run the exact camera/audio/Display/input operation and recovery script on the named pair. |
| `ODC-RELEASE-01` | `signed`/`release-channel` | Verify privacy, reviewer setup, channel, artifact identity, and user-facing disclosures. |

No source, phone-local result, mock, or browser result closes a physical
glasses-native claim. No product label closes a generation mapping.

## Sources

- [Full DAT SDK capability and source-conflict matrix](15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
- [Privacy, publishing, and release](08-privacy-publishing-and-release.md)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [Meta Wearables full reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS repository and changelog](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository and changelog](https://github.com/facebook/meta-wearables-dat-android)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
