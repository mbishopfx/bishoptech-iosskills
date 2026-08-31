# Meta Wearables role routing

Use the narrowest set of roles that can prove the requested behavior. The roles are complementary; they are not permission to invent unsupported APIs.

The exact upstream role-to-local-owner contract lives in
[team-manifest.yaml](team-manifest.yaml); validate it before delegating a
full-SDK or cross-platform request.

| Request signal | Primary role | Required handoff | Evidence that remains separate |
| --- | --- | --- | --- |
| “Connect glasses,” “pair,” “register,” “DAT” | `meta-wearables-route-planner` then `meta-dat-ios-integration` | package/version, callback, permissions, session states | mock link vs real glasses registration |
| “Android,” “Kotlin,” “Gradle,” “Manifest,” Android DAT | `meta-dat-android-integration` | Maven artifacts, initialization, `DatResult`, `Flow`/`StateFlow`, permissions, R8, and target config | Android mock/build vs named physical glasses |
| “full SDK,” “all capabilities,” “regular SDK,” or iOS/Android parity | `meta-wearables-full-sdk-audit` | Four runtime DAT module/artifact lanes plus the iOS test-only MockDevice client, source-conflict ledger, capability/evidence-plan entries, owner routes, fallbacks, and evidence gates | source/plugin inventory vs selected target build and physical behavior |
| exact iOS import, changed Swift symbol, 0.9 migration, sample architecture, debug/MCP question | `meta-dat-api-atlas` | pinned commit/tag, iOS package products, lifecycle symbols, upstream source/tool route | source lookup vs target compile, account, or hardware proof |
| exact Android import, changed Kotlin/Java symbol, Maven artifact, Gradle/API migration, Android Display/MockDevice/debug question | `meta-dat-android-api-atlas` | pinned artifact coordinates, Android API surface, `DatResult`/`Flow` contract, migration ledger, and selected-target compile seam | source lookup vs target compile, account, or hardware proof |
| organization/team access, project/app identity, permission rationale, version/build status, tester invite, release channel, Meta AI channel, telemetry, or Developer Center recovery | `meta-wearables-developer-operations` | account/project/version/channel matrix, mode distinction, telemetry/privacy boundary, and DCO evidence rows | public guide vs authorized account state vs device/physical behavior |
| bundle/package identity, Meta AI callback, Developer Mode versus release attestation, `MetaAppID`/`ClientToken`/`APPLICATION_ID`, GitHub package credentials, signing/artifact redaction, Web App origin, App Store/privacy-manifest gate, or security-sensitive on-device claim | `meta-wearables-security-attestation` plus the selected platform/privacy/on-device role | redacted identity tuple, callback validation, mode/channel and attestation boundary, secure credential/artifact handling, processing-location handoff, and SEC evidence rows | source/configuration vs account/attestation/signing vs physical capability/local processing/review |
| new app, shared iOS/Android behavior, adapter boundary, state machine, fallback, concurrency, or test seam | `meta-wearables-app-architecture` plus the selected platform/capability role | shared domain contract, platform adapter map, lifecycle/epoch/resource ownership, phone fallback, and evidence seams | shared reducer/fake/mock/browser vs target build/physical glasses |
| concrete Swift/Kotlin/Java/Web App scaffolding, selected playbook implementation, or build handoff | `meta-wearables-implementation-recipes` plus the selected platform/capability role | source-aligned adapter shape, confirmed versus `to-verify` symbols, compile-gated target tuple, ownership/epoch/stop order, data-path/privacy contract, fallback, and next proof task | recipe/reference code vs target compilation, connected device, physical glasses, signed release, or production |
| new target setup, package/dependency inventory, build preflight, archive identity, or reproducible evidence run | `meta-wearables-device-proof` plus the selected iOS/Android/Web App integration role | `PRE-*` target inventory, resolved dependency graph, privacy/configuration summary, redacted identity, device tuple, and next build/device gate | preflight/static/build facts vs account, physical glasses, signed release, or production behavior |
| camera preview, frames, recording, vision | `meta-dat-camera-audio` | camera config, stream ownership, AVFoundation boundary, stop/cancel | generated/mock frames vs glasses camera |
| microphone, audio capture, speech input | `meta-dat-camera-audio` plus privacy role | HFP/A2DP route, AVAudioSession ordering, consent, buffering, retention | phone mic vs HFP glasses mic vs transcription output |
| Wi-Fi streaming, local-network keys, Bluetooth/link instability, audio-route failure, dropped frames, latency, thermal transport, or transport parity | `meta-wearables-transport-reliability` plus the relevant platform/camera role | transport-hop map, iOS/Android configuration matrix, bounded queue/audio policy, first failure, recovery, and TRN evidence rows | declared permission vs negotiated link; phone/mock vs physical; transport vs processing location |
| DAT cannot connect, readiness/registration/permission/device/session/stream fails, live DAT Inspector/MCP is available, or logs/diagnostics need a handoff | `meta-wearables-debugging-observability` plus the relevant platform/transport/operations role | read-only connection/readiness baseline, first-failure state, narrow event/error digest, owner hypothesis, redacted diagnostic bundle, and DBG evidence rows | debug-server connection vs SDK readiness; app-visible boundary evidence vs companion internals; logs vs physical/release proof |
| Display buttons, D-pad/captouch, Neural Band/EMG, temple gesture, IMU/motion/orientation, geolocation, browser sensors, or sensor privacy/lifecycle | `meta-wearables-input-sensors` plus `meta-dat-display`, `meta-wearables-web-apps`, privacy/on-device, and device-proof as applicable | signal-to-surface ledger, exact symbol/capability/permission/secure-context status, normalized event/epoch contract, teardown/duplicate/stale rules, fallback, and INP evidence rows | native DAT versus Web App versus phone sensor; browser/mock versus physical gesture/sensor behavior; source wording versus target capability |
| glasses Display, button, D-pad, glance UI | `meta-dat-display` | `supportsDisplay()`, view/input contract, phone handoff | native Display mock vs Display hardware |
| Ray-Ban Display HTML/JS surface | `meta-wearables-web-apps` | URL, 600×600 surface, focus/input, simulator | browser simulator vs published URL vs glasses |
| “Gen 2,” “Gen 3,” “Meta Glasses,” “Oakley,” “Ray-Ban” | full-SDK audit plus route planner and device-proof roles | product-label/SDK-identity/runtime-capability matrix, exact `DeviceType`, model, firmware, capability matrix | marketing product name vs SDK enum vs observed device |
| firmware number, companion/on-glasses DAT-app version, version-dependency table, 0.8→0.9 upgrade, Gen 2 compatibility failure, or support-matrix request | `meta-wearables-device-compatibility` plus operational-readiness and selected platform/API-atlas role | exact package/artifact/source revision, access-gated dependency state, complete compatibility tuple, first-party/community classification, capability status, firmware-drift recovery, and `COMP-*` evidence rows | public release signal vs authenticated support table vs named physical compatibility; Gen 3/“regular SDK” remains unresolved without mapping |
| App Store submission, consent, recording, data use | `meta-wearables-privacy-publishing` | permission strings, privacy manifest, terms, review notes | documentation audit vs review outcome |
| “on-device,” “local-first,” raw-data boundaries, thermal/network safety, lifecycle fallback | `meta-wearables-on-device-compliance` plus the relevant DAT/Web App role | processing-location contract, consent/data-flow matrix, bounded queues/storage, thermal/background/offline fallback | phone-local vs glasses-native vs remote vs mixed processing |
| firmware, Meta AI version, Developer Mode, release channel, DAT app on glasses, update-required/device-unavailable, thermal/power, or recovery | `meta-wearables-operational-readiness` plus device-proof and the relevant DAT role | compatibility tuple, mode/channel gate, first failing state, bounded recovery, post-action state, and redacted incident packet | Developer Mode vs release channel; attempted vs observed recovery; source signal vs physical behavior |
| SDK release, changed symbol, stale source | `meta-wearables-source-refresh` | public-ref checker output, URL, expected/observed commit or tag, date, changed API, migration note, and refresh receipt | source snapshot vs local build |
| full feature request | team lead | one route decision and one evidence ledger | each specialist’s isolated result |

## Handoff packet

Every role handoff should include:

- target repository and exact app target;
- user outcome and whether the feature is phone-first, glasses-first, or dual-surface;
- exact device/model language supplied by the user and the runtime identifier, if known;
- SDK name, package tag/commit, and official source URL;
- permissions, entitlements, privacy, and data-retention assumptions;
- lifecycle states and a fallback when the wearable is unavailable;
- processing location, network/storage boundary, retention, consent, and thermal/lifecycle fallback;
- companion/firmware/on-glasses DAT-app state, Developer Mode or release channel, compatibility, first failure, and recovery status;
- shared domain state owner, platform adapter boundary, capability owner, event epoch, cancellation, stale-event, and test seam;
- current evidence level and the next proof needed.

If a required field is unknown, label it `to-verify`; do not silently substitute a similar model or SDK.

## Machine-readable routing receipt

Run the [route receipt runner](../scripts/route_capability.py) after selecting a
capability and before writing a target handoff:

```sh
python3 ../scripts/route_capability.py \
  --capability camera-photo \
  --workspace-root <knowledge-base-workspace> \
  --json
```

Use `--full-sdk` for the composite request. The runner reads the team manifest,
source-pinned surface manifest, and capability/evidence plan, then emits the
exact selected capabilities, surfaces, local role IDs, upstream handoff IDs,
privacy/fallback contracts, `PRE-*` tasks, evidence levels, terminology
actions, source snapshot, non-claims, and next action. It is read-only and
does not resolve credentials or promote any evidence level.

## Static fixture-suite receipt

Run the [static fixture suite](../scripts/run_static_fixture_suite.py) after a
recipe or fixture change:

```sh
python3 ../scripts/run_static_fixture_suite.py <workspace-root> \
  --ios-dat-checkout <selected-dat-ios-checkout> \
  --live-source --json
```

The suite runs the dependency-free shared-domain tests, Web App Node tests and
strict metadata preflight, Android target preflight, surface/capability/team/
recipe validators, every target-intake handoff, and the composite full-SDK route receipt. The iOS option
type-checks the four portable DAT starters against the selected simulator
XCFrameworks. `unavailable` and `not-run` are preserved in the receipt; none of
these results closes connected, physical, account, signed, or release proof.

## Current route defaults

- Choose native DAT for an iOS companion app that needs supported device access through the official iOS SDK.
- Choose DAT Android for an Android companion app; do not translate Swift symbols or Info.plist keys by analogy.
- Run the full-SDK auditor before calling a dependency graph or feature list “full.”
- Choose a native DAT Display path only after the target device reports Display capability.
- Choose a Web App for a Ray-Ban Display surface that is intentionally delivered as a public HTML/CSS/JS experience.
- Keep the phone surface as the fallback and consent/control plane when the wearable route is unavailable or not yet proven.
- Treat Meta AI voice commands and a public “Gen 3” API mapping as unresolved unless a current official source and hardware evidence establish them.
- Treat “on-device” as a claim requiring an explicit processing location and evidence; a phone companion is not automatically glasses-native.

## Sources

- [Meta DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [Meta DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Full SDK capability and source-conflict matrix](../../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md)
- [Device-generation and runtime-support matrix](../../../../70-meta-wearables/16-device-generation-and-runtime-support-matrix.md)
- [On-device compliance and runtime contract](../../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md)
- [Security, attestation, and credential-boundaries route](../../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
- [Version-dependency and device-compatibility route](../../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md)
- [Meta Wearables Web App repository](https://github.com/facebook/meta-wearables-webapp)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
