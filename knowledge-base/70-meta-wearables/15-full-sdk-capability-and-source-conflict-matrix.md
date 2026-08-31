# Full DAT SDK capability and source-conflict matrix

This page defines what “full Meta Wearables SDK” means for this knowledge
base. It inventories the public mobile modules, upstream agent surfaces,
debugging/documentation routes, and Ray-Ban Display Web Apps without treating
Meta AI consumer behavior or a product-generation label as a third-party API.
Reviewed 2026-08-22 against the exact public repository snapshots recorded in
the [Meta source registry](../sources/meta-wearables-source-registry.md).
Use the [source-pinned surface manifest](27-source-pinned-surface-manifest.md)
to select the native DAT iOS, native DAT Android, Web Apps, or phone-fallback
journey and load the corresponding API-surface, module, capability, conflict,
generation, and evidence rows before making a full-surface claim.
Use the [on-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
when the request makes local-processing, privacy, thermal, storage, or
fallback claims in addition to API/module coverage.
Use the [application architecture and platform-boundaries route](19-application-architecture-and-platform-boundaries.md)
when the request spans multiple platforms, native Display, Web Apps, shared
state, or phone fallback.
Use the [Android API surface atlas](20-dat-android-api-surface-atlas.md) for
exact Android Maven artifacts, Kotlin/Java symbols, and 0.9 migration gates;
the parity rows below are not a substitute for resolving the selected target.
Use the [security, attestation, and credential-boundaries route](25-security-attestation-and-credential-boundaries.md)
when the request involves project identity, Meta AI callbacks, Developer Mode,
release-channel attestation, package/signing credentials, Web App origin
separation, or App Store/privacy-manifest gates.
Use the [version-dependency and device-compatibility route](26-version-dependency-and-device-compatibility-evidence.md)
when the request names Gen 2/Gen 3, firmware, Meta AI/on-glasses DAT-app
versions, version-dependency tables, or a compatibility failure.

Terminology note: the current raw full-reference source is the DAT SDK v0.9
route for native iOS/Android. The separate Web Apps toolkit and Developer
Center sources define the glasses-hosted lane. The repositories call the native
product the Device Access Toolkit (DAT). “Regular SDK” therefore resolves to
DAT for native regular glasses or Web Apps for hosted Display UI; it is not a
third public module family.

The raw full-reference endpoint also publishes a broader conceptual v0.9 index
(`MWDATCore`, `MWDATDevice`, `MWDATCamera`, `MWDATMedia`, `MWDATDisplay`,
`MWDATState`, `MWDATLogger`, `MWDATMock`, and `MWDATKey`). The public iOS and
Android repositories currently expose five iOS package products (four runtime
products plus the test-only `MWDATMockDeviceTestClient`) and four Android
artifacts. This matrix preserves both inventories: an indexed conceptual name
is not automatically an importable product or target symbol, and a test client
is not an app runtime capability.

## Full surface inventory

| Surface | iOS DAT 0.9.0 | Android DAT 0.9.0 | Ray-Ban Display Web Apps | Boundary |
| --- | --- | --- | --- | --- |
| Core integration | `MWDATCore` | `mwdat-core` | Not a native DAT module | Initialization, registration, permissions, devices, selectors, sessions, state, and errors are target-specific. |
| Camera/media | `MWDATCamera` | `mwdat-camera` | No public Web App camera contract established | Stream, frame, photo, and media ownership must be proved per target. |
| Native Display | `MWDATDisplay` | `mwdat-display` | Separate DOM/hosted runtime | Native Display is attached to a started DAT session and is not SwiftUI or Web App DOM. |
| Deterministic testing | `MWDATMockDevice` + `MWDATMockDeviceTestClient` | `mwdat-mockdevice` | Browser Display simulator/toolkit QA | The test client controls the iOS MockDevice localhost server from XCUITest; mock/browser results establish logic or layout only, not radio, optics, audio, firmware, or physical input. |
| Full-reference conceptual index | Broader v0.9 names including `MWDATDevice`, `MWDATMedia`, `MWDATState`, `MWDATLogger`, and `MWDATKey` | Android reference namespaces and artifact routes | Separate Web Apps toolkit/Developer Center route | Index/source evidence only; resolve the selected package/API reference before importing or promising a capability. |
| Documentation/debugging | DAT plugin roles, samples, public MCP, optional live debug tooling | DAT plugin roles, samples, public MCP, optional live debug tooling | Web Apps toolkit roles, public MCP, browser simulator | Documentation search and debug-server observations are separate evidence planes. |
| Debugging/observability specialist | Local read-only first-failure, event/error, and redacted diagnostic contract | Same contract with Android `DatResult`/state names resolved from the selected artifact | Web App docs/simulator only unless the failure crosses into native DAT or physical Display | Local role evidence is an app-visible diagnosis, not companion internals, target build, physical, or release proof. |
| Portable source-pinned surface manifest | [Machine-readable routing snapshot](27-source-pinned-surface-manifest.md) | Selects the journey and records module/artifact, capability, conflict, generation, evidence, and refresh rows | Snapshot only; exact package/API, account, target, physical, and release evidence remain authoritative. |

The mobile SDK family is five iOS package products (four runtime products plus
one test-only client) and four Android artifacts in the current public
snapshot. “Full” therefore means that an implementation has checked the
required runtime, test, camera, Display, mock, privacy, debugging, and release
surfaces for the selected target—not that every product has every capability.

## Full-reference section inventory

The DAT-filtered v0.9 reference is a journey map as well as an API index. Audit
each section below when a request says “full SDK” or “regular SDK”:

| Reference section | Local route/owner | Status boundary |
| --- | --- | --- |
| Setup, hardware requirements, glasses software, Developer Mode, integration lifecycle, sessions, and key components | [route selection](00-platform-and-route-selection.md), [device matrix](16-device-generation-and-runtime-support-matrix.md), [registration/configuration](02-registration-permissions-and-configuration.md), [operational readiness](18-operational-readiness-and-recovery.md) | Source and target gates; exact version dependencies, provisioning, and account access remain target-specific. |
| iOS integration journey: Info.plist, SPM, initialization, registration, permissions, session, camera, photo | [DAT iOS foundations](01-dat-ios-sdk-foundations.md), [API atlas](10-dat-ios-api-surface-atlas.md) | Pin the package/tag and compile the actual target; do not use the raw guide as a substitute for generated symbols. |
| Android integration journey: Manifest, Gradle/GitHub Packages, initialization, registration, permissions, session, camera, photo | [Android parity](14-dat-android-parity-and-boundaries.md) | Pin the Maven artifacts and credentials locally; Kotlin/Java and Swift signatures remain separate. |
| Native Display iOS/Android: sessions, components, input, video, lifecycle, errors, icons | [native Display](04-display-access-and-glasses-ui.md), [Display role](../skills/packages/meta-dat-display/SKILL.md) | Capability-gated and physical-display-sensitive; a frame name or mock does not prove rendering/input. |
| Session lifecycle, device availability, registration, and multi-device permissions | [session/camera/audio](03-device-session-camera-and-audio.md), [registration](02-registration-permissions-and-configuration.md) | State streams, companion, permission, link, compatibility, and teardown must be observed per target. |
| Microphones and speakers: A2DP and HFP | [camera/audio role](../skills/packages/meta-dat-camera-audio/SKILL.md), [on-device contract](17-on-device-compliance-and-runtime-contract.md) | Route-specific glasses audio; phone microphone and remote transcription are distinct claims. |
| Transport and runtime reliability: Bluetooth, Wi-Fi/local network, audio routes, backpressure, thermal/power, and recovery | [transport/reliability route](22-transport-audio-and-runtime-reliability.md), [transport role](../skills/packages/meta-wearables-transport-reliability/SKILL.md), [operational readiness](18-operational-readiness-and-recovery.md) | iOS Wi-Fi/local-network setup is source-backed; the reviewed Android 0.9 source does not establish equivalent DAT Wi-Fi parity; declared permissions, link state, and processing location remain separate. |
| Mock Device Kit iOS/Android and XCUITest/instrumentation controls | [MockDevice evidence](07-mockdevice-testing-and-evidence.md), [device proof](../skills/packages/meta-wearables-device-proof/SKILL.md) | Deterministic logic and failure evidence only; no radio, optics, HFP, firmware, or physical input proof. |
| AI-assisted development, AGENTS.md, Codex/plugin configuration, API reference, DAT MCP, and live debugging MCP | [upstream tooling map](11-upstream-skill-and-tooling-map.md), [API atlas](10-dat-ios-api-surface-atlas.md), [debugging/observability](23-debugging-observability-and-diagnostic-evidence.md) | Source lookup and optional app-visible debug route; public MCP or agent instructions do not grant account, build, companion-internal, or device authority. |
| Organization, team, project, application-ID, permissions, versions, release channels, and tester access | [privacy/publishing/release](08-privacy-publishing-and-release.md), [Developer Center operations](21-developer-center-project-and-release-operations.md), [security/attestation](25-security-attestation-and-credential-boundaries.md), [evidence packet](12-device-and-release-evidence-packet.md) | Account, organization, preview, callback, attestation, credential, release-channel, signed artifact, and production gates remain separate. |
| Web Apps journey and Web App toolkit boundary | [Web Apps route](06-web-apps-display-and-input.md), [Web Apps role](../skills/packages/meta-wearables-web-apps/SKILL.md) | Hosted MRBD route only; toolkit/full-reference conflicts remain feature-level `to-verify`. |
| Version dependency and device compatibility | [compatibility evidence route](26-version-dependency-and-device-compatibility-evidence.md), [device-generation matrix](16-device-generation-and-runtime-support-matrix.md), [operational readiness](18-operational-readiness-and-recovery.md) | Public 0.9.0 release/artifact signals do not replace the authenticated version table, exact firmware/companion tuple, or named physical result. |

This inventory deliberately includes operational and administrative sections.
An app that can import `MWDATCamera` but has not resolved permissions,
organization/project access, version dependencies, release channel, privacy,
or physical evidence is not a complete “full SDK” implementation.

## Capability matrix

| Capability | iOS DAT | Android DAT | Web Apps | Minimum useful gate |
| --- | --- | --- | --- | --- |
| Initialize/configure | `Wearables.configure()` and target `Info.plist` | `Wearables.initialize(context)` and target `Manifest`/Gradle | Public HTTPS app metadata and host runtime | Named target, SDK/artifact revision, config placeholders, and privacy files. |
| Registration/callback | Meta AI registration, URL callback, registration stream | Meta AI registration, Activity callback, `registrationState` | Add hosted URL through Meta AI | Account/app access and callback flow; source alone is not registration proof. |
| Permissions | DAT permission plus iOS usage descriptions | DAT permission plus Android runtime/Manifest permissions | Browser/host permission where the feature requests it | Permission status and denial/recovery state observed on the selected target. |
| Device discovery/selection | Devices, metadata, `AutoDeviceSelector`, `SpecificDeviceSelector` | Devices/metadata, `AutoDeviceSelector`, `SpecificDeviceSelector` | Target glasses/host installation | Runtime device identifier, link state, compatibility, and capability predicate. |
| Session lifecycle | `DeviceSession` state/error streams; terminal stop | Current examples use `Session`; 0.9 changelog names `DeviceSession` and `DeviceSession.addCamera` | Web page/app lifecycle | Resolve the exact artifact/API reference; test start, pause, doff/fold, disconnect, stop, and recreation. |
| Camera stream/photo | `MWDATCamera`, `Camera.stream`, frames, photo capture | `mwdat-camera`, `Camera.stream`, frames, photo capture | No camera API claim | Active permission, session, stream state, bounded frame consumer, and physical camera run for hardware claims. |
| Audio/microphone | Full reference documents HFP glasses-microphone input and A2DP output; iOS implementation still uses the platform audio route rather than a guessed `MWDATAudio` import. | Full reference documents HFP glasses-microphone input; the CameraAccess sound-in-video sample separately records from the phone microphone with `AudioRecord`. Resolve the exact artifact API and target route. | No Web App microphone API in the v0.9 full index | Explicit route, consent, recording/transmission policy, and physical audio observation. |
| Native Display | `MWDATDisplay`, Display DSL, ButtonGroup, video, clear/stop | `mwdat-display`, builder DSL, button groups, video, tap/click, clear/stop | Not applicable | `supportsDisplay`/`isDisplayCapable`, started session/capability, rendering/input/error test, named physical Display pair. |
| Web App display/input | Not a Web App | Not a Web App | 600×600 additive surface, D-pad/EMG toolkit guidance | Public HTTPS URL, browser simulator, then Meta AI add/launch and physical Display run. |
| Physical input/event ownership | Native Display callback surface; no dedicated public native IMU/EMG/temple event module established in this snapshot | Native Display callback surface; resolve exact artifact symbols separately | Toolkit D-pad/EMG/focus and browser motion/orientation/geolocation guidance | Name the source, capability/permission/secure-context gate, session/page epoch, teardown owner, fallback, and physical target. |
| IMU/sensors/geolocation | Public index names sensor families; exact iOS package contract remains to-verify | No equivalent native DAT sensor contract established in reviewed Android sources | Toolkit documents Generic Sensor/geolocation APIs | Permission, user gesture, target firmware, fallback, and physical source-conflict closure. |
| Wi-Fi/high-bandwidth link | DAT 0.8 adds Wi-Fi transport; current setup exposes local-network/Bonjour gates where required for camera/display | Bluetooth/Internet and target configuration; reviewed 0.9 source does not establish an iOS-equivalent DAT Wi-Fi contract | Hosted HTTPS/network path | Resolve the exact Android artifact/API and record actual route, link state, interruptions, local-network/Internet policy, and named device run. |
| Device health/compatibility/update | Device state, thermal/battery/peak-power errors, firmware/DAT-app update actions | Device state/thermal and firmware/DAT-app update actions in the public 0.7+ route | Host/URL availability only | Observe the exact state/error and complete the named update/recovery action. |
| Mock/test server | MockDeviceKit, phone/file camera feeds, permissions, gestures, XCUITest test server | MockDeviceKit, phone/file feeds, permissions, lifecycle, R8 fixtures | Browser simulator and toolkit QA | Deterministic fixture labeled `fixture`/`browser-sim`, never `physical`. |
| Live debugging | Public docs MCP plus optional local DAT Inspector/debug server | Public docs MCP plus optional local DAT Inspector/debug server | Public Web Apps docs/MCP and simulator | Redacted observed debug bundle with connection, SDK readiness, device path, permissions, errors, and event digest. |
| Crash/analytics/privacy | Crash opt-out and iOS privacy/configuration audit | Crash/analytics manifest metadata and Android privacy/configuration audit | Web storage/network/host privacy audit | Disclosure, retention, deletion, minimization, and policy review; opt-out metadata is not a privacy program. |
| Identity/attestation/callback | Bundle ID, callback, `MetaAppID`, `ClientToken`, `TeamID`, Developer Mode/release mode | Package/application ID, callback, `APPLICATION_ID`, `CLIENT_TOKEN`, Developer Mode/release mode | HTTPS origin/revision and add/launch distribution state | Redacted configuration, callback validation, attestation, signing, channel, and origin evidence; identity does not prove local processing or physical capability. |
| Version dependency/firmware compatibility | DAT iOS package/changelog and named runtime identity | DAT Android artifact/changelog and named runtime identity | Web App toolkit/reference revision plus target firmware/Display | Exact version table, phone/Meta AI/on-glasses DAT-app/firmware tuple, capability run, and recovery; retail Gen 2/Gen 3 wording is not sufficient. |
| Release/publishing | Developer preview, account/release-channel, signing/App Store gates | Developer preview, account/release-channel, signing/Play gates | Public HTTPS deployment and add-to-glasses flow | Exact build/URL/channel evidence; no approval or production claim from source. |
| Operational readiness/recovery | Companion, firmware, on-glasses DAT-app, link, thermal/power, lifecycle, update navigation, and failure diagnostics | Same concepts with Android artifact/Manifest and `DatResult` boundaries | Companion, firmware, hosted URL, Display provisioning, and target launch/exit | Compatibility tuple, first failure, bounded recovery, post-action state, and named physical/release evidence. |

## Source-conflict ledger

These are actionable conflicts, not reasons to silently choose the newest-looking
snippet. The selected artifact/API reference and a named target win for
implementation; the conflict remains visible until the source is corrected or
the target proves the behavior.

| Source pair | Conflict | Classification | Required action |
| --- | --- | --- | --- |
| iOS `AGENTS.md`/upstream Display guidance vs iOS 0.9.0 changelog | The agent guidance tells a Display app to set `MWDAT.DAMEnabled = true`; the 0.9.0 changelog says DAM is always enabled and the key is ignored. | `source-conflict`, release-sensitive | Do not add or retain the obsolete key without checking the selected package and target build; record the exact build result. |
| iOS `AGENTS.md` prerequisites vs iOS 0.9.0 changelog | The generated guidance still says iOS 16.0; the 0.9.0 changelog raises the minimum to iOS 17.2. | `stale-upstream-guidance` | Treat the pinned 0.9.0 package/changelog as the build gate and update target settings before implementation. |
| Android `getting-started`/`AGENTS.md` examples vs Android README/changelog | Some upstream examples still pin `mwdat = "0.8.0"`; the current README and changelog identify 0.9.0 artifacts/release. | `stale-upstream-guidance` | Pin the selected artifact explicitly and typecheck the exact target; do not copy the example version. |
| Android `AGENTS.md` Display section vs Android 0.9.0 changelog | The section still instructs `DAM_ENABLED=true`; the changelog says DAM is always enabled and the key is ignored. | `source-conflict`, release-sensitive | Treat the changelog/package as authority for 0.9.0 and keep the obsolete key as a migration trap until target build evidence resolves it. |
| Android current skills/AGENTS vs Android 0.9.0 changelog | Current examples call the object `Session`; the 0.9.0 changelog describes `DeviceSession.addCamera(...)` and the 0.7 migration renamed `Session` to `DeviceSession`. | `symbol-conflict` | Resolve from the generated API of the exact Maven artifact; never infer from role prose or cross-platform parity. |
| Full public reference vs Web Apps toolkit `main` | The full index says no text input, offline, back navigation, or related extended features; toolkit skills document them. | `source-conflict`, device/firmware-sensitive | Keep text, offline, back, extended gestures, and sensors `to-verify` and run each feature as an independent physical task. |
| Full public reference vs iOS 0.9.0 package | Public index and package/changelog differ on some minimum-OS/module wording. | `version-conflict` | Pin package/API reference for the target and retain the discrepancy in the refresh ledger. |
| Full-reference IMU/Web App input wording vs public DAT role trees and Web Apps toolkit | The raw index mentions IMU sensors and Web App input/sensor families, while the public native DAT trees expose no dedicated sensor role in this snapshot and the moving Web App toolkit is more specific than the full index. | `surface-conflict`, `to-verify` | Do not invent native sensor symbols or treat browser events as DAT events; keep a source-specific adapter and close `INP-*` rows with the selected artifact, runtime, simulator, and named physical target. |
| Full-reference identity/attestation wording vs moving platform setup roles | The raw reference names the iOS/Android identity keys and release attestation behavior; upstream setup roles show Developer Mode placeholders and package-access instructions that are variant- and artifact-sensitive. | `mode-conflict`, `credential-boundary` | Keep values redacted, resolve the selected package/build and authorized project, separate Developer Mode from release-channel evidence, and close `SEC-*` rows without storing secrets. |
| Authenticated version-dependency table vs public release/artifact/community signals | The version-dependency page is login-gated here; public 0.9.0 changelogs/package pages establish release availability, while a closed Gen 2 firmware report is community evidence only. | `access-gated`, `community-signal` | Record the unavailable first-party result, full compatibility tuple, and `COMP-*` rows; never derive official firmware support from an issue or retail label. |
| iOS 0.8/0.9 Wi-Fi transport signal vs Android 0.9 public setup/changelog | iOS changelog/setup explicitly describe Wi-Fi transport and local-network/Bonjour configuration; the reviewed Android source establishes Bluetooth/Internet and DAT lifecycle but not an equivalent Wi-Fi contract. | `platform-parity-conflict` | Keep Android Wi-Fi `to-verify`; resolve against the selected artifact/API reference and a named Android transport run before promising parity. |
| Full v0.9 reference vs iOS 0.9.0 changelog | The raw full reference describes iOS 15.2+/Android 10+ platform requirements and a broader conceptual module index; the iOS 0.9.0 changelog raises the iOS minimum to 17.2 and the repositories expose narrower package products. | `version-conflict`/`index-vs-package` | Use the selected package/changelog for build gates, keep the full index for capability discovery, and verify the target’s actual API surface. |

## Full-SDK audit workflow

1. Record the platform, target, OS/min SDK, exact package/artifact revision,
   Meta AI version, glasses wording, requested capability, and intended evidence
   level.
2. Inspect the actual iOS package products or Android Gradle graph. A source
   repository, plugin manifest, or broad `llms.txt` index does not prove that a
   module or symbol is available to the target.
3. Fill every requested capability row with `current`, `to-verify`,
   `source-conflict`, or `unsupported`; include the phone fallback and privacy
   owner.
4. Add a deterministic mock/browser fixture, then run the named connected or
   physical task only when account, target, firmware, and hardware exist.
5. Return a gap list. Do not call the SDK “full” if a requested camera, audio,
   Display, sensor, generation, release, or privacy claim is only inferred.

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS AGENTS.md](https://github.com/facebook/meta-wearables-dat-ios/blob/main/AGENTS.md)
- [DAT iOS 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android AGENTS.md](https://github.com/facebook/meta-wearables-dat-android/blob/main/AGENTS.md)
- [DAT Android 0.9.0 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS plugin](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios)
- [DAT Android plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [DAT Android phone-microphone sample](https://github.com/facebook/meta-wearables-dat-android/blob/main/samples/CameraAccess/app/src/main/java/com/meta/wearable/dat/externalsampleapps/cameraaccess/stream/AudioInputHandler.kt)
- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT-filtered full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
