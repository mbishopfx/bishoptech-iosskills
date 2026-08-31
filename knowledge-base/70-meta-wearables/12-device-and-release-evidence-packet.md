# Meta Wearables device and release evidence packet

Use this packet when a Meta Wearables result could be mistaken for glasses,
radio, camera, audio, Display, input, release-channel, or production proof. It
is an execution plan, not a record that these tests have already run.

Read the [device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
before assigning a product label to a target. A consumer generation name is
not a substitute for runtime model identity, capability response, firmware, or
physical evidence.

## Status vocabulary

Use exactly one status per task:

| Status | Meaning |
| --- | --- |
| `source` | An official source documents the route or constraint. |
| `static` | The target/package/configuration was inspected. |
| `build` | The selected target compiled or a deterministic test ran. |
| `mock` | DAT MockDevice controlled the state or media fixture. |
| `browser-sim` | The Web App browser simulator exercised the hosted-surface logic. |
| `connected` | A named paired device completed the operation, but the run is not yet a physical release proof. |
| `physical` | The exact named glasses completed the scripted operation with a sanitized artifact. |
| `signed` | The exact signed build and entitlements were inspected and installed/exercised. |
| `release-channel` | The exact build was delivered through the documented Meta tester/channel path. |
| `production` | The operation was observed in the live production environment. |
| `not-run` / `blocked` / `to-verify` | The step remains open; do not infer success from an adjacent level. |

## Target preflight before device work

Before `BUILD-01`, `REL-01`, connected, physical, or release-channel work, use
the portable [target-preflight reference](../skills/packages/meta-wearables-device-proof/references/target-preflight.md). It freezes the actual iOS scheme/target and `Package.resolved`, Android module/variant and resolved Maven graph, or Web App revision/origin/input configuration. The preflight is an evidence gate, not a claim upgrade: it cannot prove a named pair can register, render, stream, capture, hear, or accept input.

Record `PRE-SOURCE-01`, the platform-specific `PRE-IOS-01`,
`PRE-ANDROID-01`, or `PRE-WEB-01`, then `PRE-IDENTITY-01`, `PRE-DATA-01`,
`PRE-TUPLE-01`, and `PRE-BUILD-01` as applicable. Keep credentials and raw media
out of the record; unknown generation, firmware, account, and processing values
remain `to-verify`, `access-gated`, or `not-run`.

## Run identity and artifact contract

Create one sanitized run directory per target and build:

```text
artifacts/meta-wearables/<run-id>/
  manifest.md
  static/target-inventory.txt
  build/<bundle-id>-<version>-<build>.xcarchive
  logs/<task-id>.redacted.log
  screenshots/<task-id>-<step>.png
  results/<task-id>.md
```

Use a run ID such as
`mwdat-20260822-ios-rb-display-build42`; never put a serial number, email, or
access token in the name. Every `results/<task-id>.md` must state:

```text
Task ID:
Status:
Route: native-DAT | native-Display | Web-App | phone-fallback
Source/package revision:
Target/scheme:
Bundle ID and version/build:
iOS and phone:
Consumer product/model:
Runtime DeviceType:
Glasses firmware / DAT-on-glasses version:
Meta AI companion version:
Account/channel condition: dev-mode | tester | release-channel | not available
Operation exercised:
Observed result:
Artifacts:
Negative cases:
What this proves:
What this does not prove:
Next gate:
```

Redact callback query values, client tokens, Meta project IDs when not needed
for diagnosis, serials, MAC/device identifiers, email addresses, raw photos,
raw video, raw audio, transcripts, and personal Display content. Store hashes,
counts, dimensions, sample rates, error categories, and sanitized screenshots
instead. Do not place any of these values in a skill archive.

## Device matrix before execution

| Test label | Product wording | Runtime/API identity | Required treatment |
| --- | --- | --- | --- |
| `rb-meta-gen1` | Ray-Ban Meta Gen 1 | Record the observed current `DeviceType` | Run only if the selected public DAT release and firmware list it as supported. |
| `rb-meta-gen2` | Ray-Ban Meta Gen 2 | Record the observed current `DeviceType` and capability response | Gen 2 evidence does not generalize to another generation or model. |
| `rb-meta-optics` | Ray-Ban Meta Optics | Record the observed current `DeviceType` | Camera/audio/display capabilities remain runtime and firmware gates. |
| `mrbd` | Meta Ray-Ban Display | Record `supportsDisplay()`/equivalent and the observed model | Required for native Display and physical Neural Band/Display proof. |
| `oakley-or-meta-enum` | Oakley Meta or other enum-listed Meta glasses | Record exact model, firmware, and capability response | An SDK enum or product name alone is not hardware proof. |
| `meta-glasses-to-verify` | Meta Glasses product line; may be what a user calls “Gen 3” | Record the observed current `DeviceType` and product/firmware identity | Do not alias the product announcement or `.metaGlasses` to a generation without target evidence. |
| `gen3-to-verify` | User-supplied “Gen 3” wording | No public mapping in this source snapshot | Keep every task `to-verify`; never alias it to `.metaGlasses`, `.rayBanMeta`, or Display. |

## Execution matrix

Run the rows that match the requested route. A row is `pass` only when its
observable operation and required evidence level are present.

| Task ID | Route | Observable operation | Minimum evidence | Stop condition |
| --- | --- | --- | --- | --- |
| `GEN-SRC-01` | all | Freeze the product label, DAT package/artifact revision, changelog, Web Apps revision, and Developer Center access state. | `source` | The product label or source snapshot is ambiguous. |
| `GEN-STATIC-01` | native DAT | Inspect actual iOS package products or Android Gradle artifacts and record model/capability symbols used by the target. | `static`/`build` | A product announcement or SDK enum is being treated as hardware proof. |
| `GEN-CONNECTED-01` | native DAT | Pair the named target and record runtime identity, firmware, companion version, link, permission, compatibility, and capability state. | `connected` | Model identity or firmware is unknown. |
| `GEN-PHYSICAL-01` | native DAT/Web App | Exercise the requested camera/audio/Display/input operation plus denial, disconnect, doff/fold, and recovery cases. | `physical` | The operation is represented by source, mock, simulator, or browser evidence only. |
| `GEN-CROSS-01` | native DAT/Web App | Repeat the same script on Gen 2 and any alleged Gen 3 target without substituting labels. | `physical` per target | Results are generalized across generations or models. |
| `ODC-SOURCE-01` | all | Freeze the DAT/Web Apps source, policy, product, package/artifact, and version snapshot used for the compliance claim. | `source` | “On-device” or “local-first” is used without a dated route/source record. |
| `ODC-STATIC-01` | native DAT/Web App | Inspect processing location, permissions, privacy metadata, network destinations, storage/logging, model/runtime symbols, and typed fallback in the actual target. | `static`/`build` | A phone-local, remote, or unknown path is described as glasses-native. |
| `ODC-MOCK-01` | native DAT/Web App | Exercise denial, disconnect, stale state, stop, fallback, loading, error, focus, and cache behavior without personal media. | `mock`/`browser-sim` | A deterministic result is promoted to physical or release proof. |
| `ODC-PHYS-01` | native DAT/Web App | Run the exact camera/audio/Display/input operation and recovery script on the named pair; record processing location and network state. | `connected`/`physical` | The target, firmware, operation, or data path is unknown. |
| `ODC-RELEASE-01` | release | Verify artifact identity, permissions/privacy disclosures, reviewer setup, account/channel, retention/deletion wording, and user-visible fallback. | `signed`/`release-channel` | Release readiness is declared while the compliance or policy gate is open. |
| `OPS-SOURCE-01` | all | Re-open changelogs, raw reference, version dependencies, known issues, and release guidance; record revision/date and access-gated values. | `source`/`access-gated` | A compatibility or recovery decision relies on an unreviewed version table. |
| `OPS-CONFIG-01` | native DAT/Web App | Validate package/artifact, deployment/min SDK, callback, permissions, privacy, signing mode, and mode-specific configuration without exposing secrets. | `static`/`build` | Developer Mode configuration is presented as release configuration. |
| `OPS-PAIR-01` | native DAT/Web App | Record companion, account/mode, runtime model, firmware, on-glasses DAT-app state, link, compatibility, and capability metadata for a named pair. | `connected`/`physical` | A missing tuple field is filled by a neighboring model or stale source. |
| `OPS-RECOVERY-01` | native DAT/Web App | Execute one scripted provisioning, update, disconnect, lifecycle, or registration recovery path and record first error, action, post-state, and original-operation result. | `physical`/`system` | A retry loop hides the first terminal, thermal, power, or unknown-protocol signal. |
| `OPS-THERMAL-01` | native DAT | Observe thermal, battery, peak-power, doff/fold, and terminal-stop behavior for the actual camera/audio/display workload. | `physical` | Source, mock, or a short compile run is used as safety proof. |
| `OPS-CHANNEL-01` | release | Install and exercise the exact signed build through the named release channel with tester account and firmware tuple. | `signed`/`release-channel` | Account, signature, application ID, channel, or build identity is unconfirmed. |
| `ARCH-SOURCE-01` | all | Freeze the selected DAT/Web App sources, package/artifact revision, and the shared/platform boundary used by the architecture. | `source` | A common abstraction hides a platform or version difference. |
| `ARCH-STATIC-01` | all | Inspect target/module boundaries, adapter imports, configuration, privacy metadata, state owner, fallback, resource owner, and session epoch. | `static` | SDK imports leak into views/domain or resource ownership is ambiguous. |
| `ARCH-TEST-01` | all | Exercise shared reducer, platform fake, cancellation, stale epoch, duplicate intent, and terminal cleanup fixtures. | `build`/`fixture` | Tests only the happy path or use platform objects in shared tests. |
| `ARCH-MOCK-01` | native DAT/Web App | Run DAT MockDevice/browser simulator through registration, denial, disconnect, unsupported, media/Display stop, and fallback. | `mock`/`browser-sim` | Mock/browser output is presented as physical behavior. |
| `ARCH-PHYS-01` | native DAT/Web App | Run the selected capability script on the named target pair with exact model, firmware, companion, build, and operation metadata. | `connected`/`physical` | Architecture is generalized across models or generations. |
| `ARCH-RELEASE-01` | release | Repeat architecture-critical flows through the signed release channel and record fallback/recovery. | `signed`/`release-channel` | Developer Mode or a shared reducer is treated as release proof. |
| `AND-SOURCE-01` | Android DAT | Freeze the four Maven artifact coordinates, Android repository revision, changelog, and Android API-reference access state. | `source` | A moving upstream example is treated as the resolved artifact. |
| `AND-CONFIG-01` | Android DAT | Validate GitHub Packages path, manifest metadata, callback, permissions, target SDK, privacy, and release-mode configuration without exposing credentials. | `static`/`build` | Developer placeholders are presented as release credentials. |
| `AND-API-01` | Android DAT | Resolve session, camera, Display, `DatResult`, and `Flow`/`StateFlow` symbols against the selected artifact or compile fixture. | `static`/`build` | iOS names, `AGENTS.md`, or source prose are treated as Kotlin proof. |
| `AND-MIGRATE-01` | Android DAT | Exercise the 0.9 camera-consolidation, Display-builder/tap, Java-visible-result, DAM, removed-error, and R8 migration checks. | `build`/`fixture` | A source migration note is treated as target compatibility. |
| `AND-MOCK-01` | Android DAT | Run MockDevice registration, permission, lifecycle, phone/file media, and input fixtures with explicit terminal cleanup. | `mock` | Mock output is treated as Bluetooth, optics, HFP, firmware, or thermal proof. |
| `AND-BUILD-01` | Android DAT | Build/test debug and release variants, minified/R8 output, and Java interop when in scope; retain redacted logs only. | `build`/`signed` | A successful build proves device or release-channel behavior. |
| `AND-PHYS-01` | Android DAT | Run the named camera/photo/Display/input/audio operation on the exact glasses, firmware, Meta AI version, app build, and companion state. | `connected`/`physical` | Another model, mock, or “Gen 3” alias is substituted. |
| `AND-RELEASE-01` | Android release | Install and exercise the exact signed APK through the named release channel with tester/account and compatibility tuple. | `signed`/`release-channel` | Play approval, production behavior, or a Developer Mode run is inferred. |
| `DCO-SOURCE-01` | Developer Center | Reopen operations/reference pages and record retrieval date, revision, and authenticated-access state. | `source`/`access-gated` | Public documentation is treated as current account state. |
| `DCO-ORG-01` | account/team | Resolve the existing MMA organization, Wearables team, and operator role. | `account` | A new organization or duplicate team is created to bypass access. |
| `DCO-PROJECT-01` | project/configuration | Inspect platform app identity, product listing, permission justification, callback, and build configuration. | `account`/`static` | Configuration proves target compilation or device behavior. |
| `DCO-VERSION-01` | version/build | Record Major/Minor/Patch intent and generated DAT application build status. | `account`/`release` | `Ready` proves tester acceptance or physical capability. |
| `DCO-CHANNEL-01` | release channel | Record channel, selected version, invite mode, tester list, and channel access. | `account`/`release-channel` | Channel creation proves registration or production. |
| `DCO-TESTER-01` | tester/device account | Observe tester Meta Account acceptance, Meta AI channel, and connected-app permissions. | `account`/`connected` | Permission state proves camera/audio/Display success. |
| `DCO-TELEMETRY-01` | telemetry/privacy | Record telemetry categories, opt-out metadata, disclosure, retention, and deletion. | `static`/`release` | Opt-out metadata is treated as a complete privacy program. |
| `DCO-RECOVERY-01` | operations recovery | Execute one bounded account/build/channel recovery and record first failure and post-state. | `account`/`release-channel` | An unobserved retry or documentation step is called recovery proof. |
| `TRN-SOURCE-01` | transport | Freeze iOS/Android transport sources, current MCP lookup, retrieval date, and Wi-Fi/HFP/A2DP claims. | `source`/`access-gated` | A moving source or iOS-only signal is treated as cross-platform support. |
| `TRN-CONFIG-01` | transport/configuration | Inspect iOS Bluetooth/local-network/Bonjour/audio configuration and Android Bluetooth/Internet/Manifest/artifact configuration without exposing credentials. | `static`/`build` | Declared permissions are treated as negotiated transport or processing proof. |
| `TRN-LINK-01` | link/transport | Observe registration, Bluetooth/control link, Wi-Fi/local-network negotiation, timeout, route change, and reconnect on the named target. | `connected`/`physical` | A connected or registered device is treated as camera, Display, HFP, or Wi-Fi capability proof. |
| `TRN-AUDIO-01` | HFP/A2DP | Exercise HFP input and A2DP output independently; record route, sample format, interruption, and restoration. | `physical` | Phone mic, remote transcription, or A2DP output is called glasses microphone input. |
| `TRN-STREAM-01` | camera/Display | Run a bounded camera/Display workload, record drops/latency/stop, then disconnect and recover. | `physical` | A mock, browser, or short compile proves sustained transport reliability. |
| `TRN-THERMAL-01` | safety | Observe thermal, battery, peak-power, doff/fold, pause, and terminal-stop behavior for the exact workload. | `physical` | Source, mock, or another model is used as safety proof. |
| `TRN-RECOVERY-01` | recovery | Apply one documented least-invasive transport recovery and repeat the original operation with a new run identity. | `connected`/`physical` | A retry loop or unobserved documentation step is called recovery proof. |
| `TRN-PHYSICAL-01` | named target | Repeat the transport/capability script with exact model, firmware, companion, app build, and mode/channel. | `physical` | The result is generalized to a generation or neighboring model. |
| `TRN-RELEASE-01` | release | Repeat critical transport and fallback flows from the exact signed release channel. | `signed`/`release-channel` | Developer Mode, source, or physical debug evidence is called release proof. |
| `DBG-SOURCE-01` | debugging | Freeze the official iOS/Android debugging and live-DAT-MCP role revisions, retrieval date, and local-server availability. | `source`/`access-gated` | A source procedure is treated as target diagnosis. |
| `DBG-CONN-01` | debugging | Discover/connect to the local DAT Inspector and record connection status with app/build label. | `connected`/`not-run` | Debug-server connection is treated as SDK or glasses readiness. |
| `DBG-READINESS-01` | debugging | Capture connection, SDK state, and DAT readiness before deeper diagnosis. | `connected`/`not-run` | A later stream symptom replaces the first readiness failure. |
| `DBG-BOUNDARY-01` | debugging | Inspect app-visible companion, permission, device, and configuration diagnosis without mutating state. | `connected`/`not-run` | App-visible events are called companion internals or successful recovery. |
| `DBG-PATH-01` | debugging | Trace registration, permission, device selection/link, session, and capability states for one target/build. | `connected`/`physical` | The path is generalized to another model, firmware, or generation. |
| `DBG-EVENT-01` | debugging | Reproduce one bounded failure and collect a narrow event/error digest plus the first failing state. | `connected`/`physical` | Unbounded polling or generic logs hide the first failure. |
| `DBG-BUNDLE-01` | debugging | Export a diagnostic bundle, inspect it, and record whether the handoff is redacted. | `connected`/`not-run` | Raw media, tokens, identifiers, or personal data enter the artifact. |
| `DBG-REDACTION-01` | privacy/debugging | Verify removed fields, stable local labels, retention, and deletion for the redacted bundle. | `static`/`account` | Redaction is treated as legal/privacy approval. |
| `DBG-PHYSICAL-01` | debugging/physical | Correlate the app-visible diagnosis with a named pair, firmware, task, and physical camera/audio/Display/input result. | `physical` | A debug bundle alone is called physical hardware proof. |
| `DBG-RELEASE-01` | debugging/release | Repeat the critical diagnostic operation from the exact signed release-channel build. | `signed`/`release-channel` | Developer Mode or a debug build is called release/production proof. |
| `INP-SOURCE-01` | input/sensors | Freeze DAT iOS/Android Display sources, Web Apps toolkit/full-reference revisions, target-device wording, and conflict status. | `source`/`access-gated` | A conceptual IMU or gesture label is treated as an importable API. |
| `INP-STATIC-01` | input/sensors | Inspect target imports, capability/permission/secure-context gates, listener/watch ownership, event epoch, privacy metadata, and processing-location declaration. | `static`/`build` | A browser API, native Display callback, or phone sensor is silently substituted for another surface. |
| `INP-MOCK-01` | input/sensors | Exercise duplicate, stale, denied, unsupported, stop, timeout, no-sensor, and phone-fallback events in a deterministic fixture. | `mock`/`fixture` | Mock events prove physical captouch, EMG, gesture timing, or sensor quality. |
| `INP-BROWSER-01` | Web App input/sensors | Run the browser simulator and deployed HTTPS page at 600x600 through focus, D-pad/Enter, source-conflicted back/gesture/text/sensor rows, and fallback. | `browser-sim` | Browser behavior is called physical MRBD behavior. |
| `INP-CONNECTED-01` | input/sensors | Record the named companion/device/link/firmware/app tuple and app-visible input/capability state. | `connected` | Registration or a connected link proves sensor quality or gesture recognition. |
| `INP-PHYSICAL-01` | input/sensors/physical | Run the exact Display/D-pad/EMG/temple/sensor script on named glasses and record action, latency/quality, comfort, processing location, and fallback. | `physical` | Gen 2, Gen 3, Display, or a neighboring model is used as a substitute. |
| `INP-RECOVERY-01` | input/sensors/recovery | Deny permission, disconnect, inject a stale event, stop a sensor watch, apply one least-invasive recovery, advance the epoch, and repeat the original action. | `connected`/`physical` | A retry loop or source note is called recovery proof. |
| `INP-RELEASE-01` | input/sensors/release | Repeat the critical input/sensor flow and privacy/fallback behavior with the exact signed release-channel build and target tuple. | `signed`/`release-channel` | Developer Mode, debug build, or simulator is called release proof. |
| `SEC-SOURCE-01` | security/attestation | Freeze the official full-reference and DAT iOS/Android setup/permissions sources, repository revisions, selected package/artifact, Apple review links, retrieval date, and source conflicts. | `source`/`access-gated` | A source recipe is called current account, secret, attestation, signing, or release behavior. |
| `SEC-STATIC-01` | security/configuration | Inspect bundle/package/application ID, callback scheme/host, iOS `AppLinkURLScheme`/`MetaAppID`/`ClientToken`/`TeamID`, Android `APPLICATION_ID`/`CLIENT_TOKEN`, build variant, privacy metadata, and signing inputs with values redacted. | `static`/`build` | Presence of keys proves validity, attestation, channel access, physical capability, or local processing. |
| `SEC-CREDENTIAL-01` | security/credentials | Verify package/client/signing secrets remain in the approved environment or secure build configuration; scan logs, fixtures, screenshots, generated output, and archives for leaked values or raw payloads. | `static`/`build` | A clean scan proves credential validity or account authorization. |
| `SEC-CALLBACK-01` | security/callback | Exercise owned callback scheme/host, malformed/unexpected/stale/duplicate rejection, SDK handoff, environment separation, and no raw URL/query/fragment logging. | `fixture`/`build`/`connected` | Callback receipt proves registration, permission, session, or physical capability. |
| `SEC-ATTEST-01` | security/attestation | Observe the release-mode project identity and attestation result for the exact signed mobile build, with credentials and identifiers redacted. | `account`/`signed`/`release-channel` | Attestation proves local processing, physical hardware, or public approval. |
| `SEC-DEVMODE-01` | security/Developer Mode | Observe Developer Mode enablement, placeholder behavior, and local registration on the named target. | `connected` | Developer Mode proves attested release, signed distribution, tester access, or production. |
| `SEC-CHANNEL-01` | security/release-channel | Observe the exact signed build, project version, invite-only channel, tester Meta Account state, Meta AI connection, and channel-selected identity. | `account`/`signed`/`release-channel` | Channel access proves camera/audio/Display/sensor behavior, App Store/Play approval, or physical capability. |
| `SEC-PHYSICAL-01` | security/physical | Repeat the security-sensitive registration/callback/identity-dependent operation on the named device, firmware, Meta AI version, companion state, and app build with redacted evidence. | `physical` | Another model, generation, or “Gen 3” alias is substituted; processing location is inferred. |
| `SEC-RELEASE-01` | security/publishing | Check current Meta/App Store/Play release eligibility and exact distribution result for the selected path, including the dated DAT App Store warning and Apple privacy-manifest/MFi review gate. | `signed`/`release-channel`/`TestFlight`/`App Store`/`production` | One source snapshot establishes permanent policy, broad availability, or production behavior. |
| `COMP-SOURCE-01` | compatibility | Freeze DAT iOS/Android changelogs, package/artifact registry, full-reference and version-dependency URLs, retrieval date, access state, and first-party/community classification. | `source`/`access-gated` | A source snippet or community issue is called official compatibility policy. |
| `COMP-STATIC-01` | compatibility/configuration | Inspect exact iOS package products or Android artifacts, target minimums, migration symbols, configuration, model/capability symbols, and Web App revision. | `static`/`build` | A retail label or upstream role name is treated as target API or hardware support. |
| `COMP-VERSION-01` | compatibility/version | Record the authenticated version-table result, or the explicit login/access-gated outcome; never fill missing app/firmware values from memory. | `static`/`access-gated` | Search snippets, a community issue, or an old table is treated as current first-party support. |
| `COMP-TUPLE-01` | compatibility/device | Record product/SKU, observed `DeviceType`, phone OS/build, Meta AI version, on-glasses DAT-app version, firmware, link, compatibility, permission, artifact, and account mode. | `connected` | Registration or a retail “Gen 2/Gen 3” label is treated as a complete compatibility tuple. |
| `COMP-CAPABILITY-01` | compatibility/physical | Run each requested camera/photo, HFP/A2DP, native Display/input, Web App launch/input, update, disconnect, and recovery operation on the named pair and record path/result. | `physical` | A version number, capability enum, connected state, mock, or browser run is generalized to every capability. |
| `COMP-FIRMWARE-01` | compatibility/recovery | Compare before/after firmware and full tuples, record the first failure, exact error, bounded recovery, and post-state; classify public issue reports as community signals. | `physical`/`source` | A single device error proves universal firmware incompatibility or a fix. |
| `COMP-GEN3-01` | compatibility/generation | Capture an official current mapping, observed runtime identity, firmware, and repeated named operation before declaring Gen 3 support. | `source`/`physical` | `.metaGlasses`, `.rayBanMeta`, Display, or a product announcement is used as a Gen 3 alias. |
| `COMP-RELEASE-01` | compatibility/release | Repeat the compatibility-critical operation from the exact signed build/channel and record tester/account/version state. | `signed`/`release-channel` | Developer Mode, local build, or channel creation is called release compatibility proof. |
| `SRC-01` | all | Freeze DAT tag/commit, Web App revision, retrieval date, and target package resolution. | `source` + `static` manifest | Package revision or API surface is ambiguous. |
| `CFG-01` | native DAT | Inspect package products, URL callback, Meta AI query scheme, background/local-network keys, usage descriptions, entitlements, privacy manifest, and fallback. | `static` target inventory | Target contains a stale key, missing disclosure, or an unverified product name. |
| `MOCK-01` | native DAT | Mock registration/permission denial, grant, pair, fold/doff/power-off, disconnect, stop, and reconnect reducers. | `mock` result and deterministic assertions | A mock state is reported as account or glasses behavior. |
| `MOCK-02` | native DAT | Mock camera frame/photo, slow consumer, cancellation, and clean `Camera.stop()`/session stop. | `mock` result with counts/dimensions only | Raw personal media enters logs or fixtures. |
| `MOCK-03` | native Display | Mock unsupported capability, Display content, ButtonGroup/action, clear, and disconnect. | `mock` result | Mock brightness, optics, Neural Band, or physical latency is claimed. |
| `WEB-SIM-01` | Web App | Run the browser simulator at 600×600 through load, focus, arrow/Enter input, additive preview, long content, loading, timeout, and error. Add separate `to-verify` rows for the toolkit-described text composer, offline cache, Escape/back, sensors, and extended gestures because the public index conflicts with toolkit `main`. | `browser-sim` recording/screenshot plus feature-level status | A simulator result is labeled as glasses delivery, or a source-conflicted feature is called supported without target evidence. |
| `BUILD-01` | native DAT | Build the selected app/test target against the pinned package and record actual products/symbols. | `build` log and test result | The package does not resolve or the code uses a removed 0.9 API. |
| `DAT-REG-01` | native DAT | From an unregistered state, start registration, complete Meta AI, return through a cold launch and warm callback, then repeat cancel/deny. | `physical` or `connected` named-device run | Callback is treated as permission or session proof. |
| `DAT-SES-01` | native DAT | Select the named device, inspect link/compatibility/permission state, start a session, pause, stop, disconnect, and reconnect. | `connected`; `physical` for release claim | Model, firmware, app version, or state transition is unknown. |
| `DAT-CAM-01` | native DAT | Start camera, observe frame metadata/counts, capture one photo, apply slow-consumer handling, stop camera, stop session, and verify no stale frames continue. | `physical` for camera claim | Phone/mock frames are presented as glasses capture. |
| `DAT-AUD-01` | native DAT | Exercise A2DP playback separately; for HFP configure the documented iOS audio route, verify `bluetoothHFP` input and 8 kHz mono metadata, stop, and restore the prior route. | `physical` for glasses-audio claim | Phone mic, remote transcription, or A2DP output is called raw glasses microphone input. |
| `DAT-DISP-01` | native Display | On a Display-capable named pair, render a compact card, exercise ButtonGroup/focus/primary action/clear, then test timeout and disconnect fallback. | `physical` | `supportsDisplay()` is missing, false, or unobserved. |
| `WEB-PHYS-01` | Web App | Add the public HTTPS URL through Meta AI, launch on the named MRBD pair, verify 600×600 legibility/focus/input, then test loading/error/exit. If in scope, independently exercise text composer, offline cache, Escape/back, sensors, and extended gestures and record each as a source-conflict closure attempt. | `physical` + hosted URL manifest | Localhost, QR, browser simulation, or a toolkit-only feature note is treated as delivery proof. |
| `REC-01` | native DAT/Web App | Repeat the requested route with glasses absent, Bluetooth/Wi-Fi/local-network denied, permission denied, stale session, timeout, low battery/thermal warning, and companion termination. | `connected`/`physical` negative-case matrix | The phone has no useful fallback or failure state is hidden behind a spinner. |
| `REL-01` | release | Inspect archive bundle ID/version/build/device family, signed entitlements, privacy metadata, Meta project/channel, tester access, install the exact build, and rerun the required task IDs. | `signed` + `release-channel` | Any secret is exposed, build identity differs, or channel/eligibility is not confirmed. |
| `PROD-01` | production | Exercise only after signed/channel gates pass and record the live URL/service/environment and exact operation. | `production` | A local build, TestFlight, or source page is called production proof. |

## Route-specific observations

For camera, record resolution, frame rate, codec, observed frame dimensions,
drop/backpressure behavior, photo result category, stop latency, and thermal or
battery notes. For HFP, record the audio route, sample rate/channel count,
interruption/route-change behavior, visible recording state, and whether any
transcription was local or remote. For Display, record capability response,
content length, focus/action outcome, clear behavior, disconnect behavior, and
physical legibility. For Web Apps, record URL revision, HTTPS result, viewport,
focus order, input mapping, network/storage behavior, and separate status rows
for camera, microphone, notifications, text composer, offline cache, back
navigation, extended gestures, and sensors. The current full-reference index
marks several of these unsupported while toolkit `main` documents others;
preserve both source observations and use `source-conflict`/`to-verify` until
the exact runtime and physical MRBD run close the gap.

## Release decision

Do not use a single green row as a release decision. The smallest honest result
is a set of claims whose status matches the strongest row actually completed:

```text
source -> static -> build/mock/browser-sim -> connected -> physical
  -> signed -> release-channel -> production
```

If a named device, account, release channel, or target build is unavailable,
leave the affected rows `not-run` or `blocked`, name the exact next gate, and
ship only the phone fallback or the lower-evidence prototype that the product
has explicitly approved.

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta DAT iOS MockDevice testing](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md)
- [Meta Mock Device Kit](https://wearables.developer.meta.com/docs/mock-device-kit)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Meta Wearables terms](https://wearables.developer.meta.com/docs/terms)
- [Wearables version dependencies](https://wearables.developer.meta.com/docs/version-dependencies)
- [Wearables known issues](https://wearables.developer.meta.com/docs/knownissues)
- [Wearables release-channel setup](https://wearables.developer.meta.com/docs/develop/dat/set-up-release-channels/)
- [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS permissions and registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md)
- [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md)
- [DAT Android permissions and registration](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/permissions-registration/SKILL.md)
- [Target preflight reference](../skills/packages/meta-wearables-device-proof/references/target-preflight.md)
- [Apple target build settings](https://developer.apple.com/documentation/xcode/configuring-the-build-settings-of-a-target/)
- [Apple Swift package CI/build guidance](https://developer.apple.com/documentation/xcode/building-swift-packages-or-apps-that-use-them-in-continuous-integration-workflows)
- [Gradle dependencyInsight](https://docs.gradle.org/current/userguide/command_line_interface.html)
- [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory)
- [Apple running apps on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
- [Apple testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
