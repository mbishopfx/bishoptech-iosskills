# Existing target intake and preflight receipt

This receipt connects the Meta Wearables team to the existing Tiny Detour
(`bishoptech-sidequest`) sibling target without changing that project. It is a
redacted routing artifact: the target's simulator build/test evidence is
recorded below through the portable device-proof runner, while connected and
physical glasses behavior remains open.

## Selected target

| Field | Observed static value | Evidence boundary |
| --- | --- | --- |
| Project | `sibling/bishoptech-sidequest` | Actual sibling target inspected 2026-08-22; private absolute path intentionally omitted from the portable receipt. |
| Surface scan | `TARGETS_PRESENT`; an iOS target and generic local web surface are detected; Android target absent | Structural target evidence only. The Web App preflight classifies the selected HTML surface as generic because Meta markers and hosted HTTPS delivery are not proven. |
| iOS target | `SideQuest` in `SideQuest.xcodeproj`; `SideQuestTests` and `TinyDetourActivity` are also declared | `xcodebuild -list -json` passed and returned all three targets. |
| Deployment/toolchain | iOS 26.0 in `project.yml`; Xcode 26.4 and Swift 6.3 installed; project Swift setting 6.2 | `xcodebuild -showBuildSettings` passed for Debug; simulator SDK was iPhoneSimulator 26.4. |
| DAT package | `MetaWearablesDAT` exact version `0.9.0`; `Package.resolved` pins revision `9b1b83d791dfebff7afd452e924a256819094b64` | Resolved-lockfile evidence; generated API compilation remains open. |
| DAT products | `MWDATCore`, `MWDATCamera`, `MWDATDisplay` | Target wiring/static evidence; no MockDevice product is linked in this target. |
| Privacy/configuration | `PrivacyInfo.xcprivacy`, Bluetooth/local-network/microphone descriptions, `com.meta.ar.wearable`, MWDAT analytics/crash opt-outs | Redacted plist/static evidence; account and runtime behavior remain open. |
| Static syntax/config QA | Swift parse `SWIFT_PARSE_OK`; 9/9 target wiring checks; three plist files lint `OK` | Static evidence; build/test evidence is recorded separately. |
| Build/test | `run_ios_target_preflight.py --test` passed; its `xcodebuild test` observation reported 65 tests in 3 suites on the iOS 26.4 simulator | Build/simulator evidence only; no glasses, account, physical, signed, or release proof. |
| Product route | Native Display when `supportsDisplay()` is true; phone/audio fallback otherwise | Source/code-routing evidence; named runtime capability remains open. |

The validated implementation handoff is
[tiny-detour-ios-implementation-handoff.yaml](target-intakes/tiny-detour-ios-implementation-handoff.yaml).
It resolves 12 manifest API rows, 17 evidence tasks, and 13 local owner roles.

## Evidence receipt

| Task | Status | Observation |
| --- | --- | --- |
| `PRE-SOURCE-01` | source receipt | Surface manifest revision 4; live source revision receipt `CHECKS 5 DRIFT 0` and live source-tree receipt `CHECKS 23 DRIFT 0` both pass in the current run. |
| `PRE-IOS-01` | static | Project, target, package lock, product wiring, privacy manifest, redacted configuration, Swift parse, plist lint, and the portable runner's `xcodebuild -list`/Debug `-showBuildSettings` checks passed. |
| `PRE-WEB-01` | static/not-ready | The Web App runner parsed the selected local entrypoint and passed Node syntax checking for its local script, but classified it as `generic-web-surface`; Meta metadata markers and hosted HTTPS delivery are not proven. |
| `PRE-IDENTITY-01` | static | Bundle/callback/privacy keys and signing configuration locations inspected with credential values redacted. |
| `PRE-DATA-01` | static | Phone-local processing, consented transient gateway path, raw-frame/audio boundary, retention, deletion, thermal, disconnect, and fallback are captured in the handoff packet. |
| `PRE-TUPLE-01` | not-run | Physical phone OS, Meta AI version, on-glasses DAT-app, firmware, runtime identity, and channel were not captured. |
| `PRE-BUILD-01` | build/test | The portable runner resolved `MetaWearablesDAT @ 0.9.0`, built the DAT/core/app/test graph, and passed 65 tests in 3 suites on the iOS 26.4 simulator. |
| Native Display recipe | compile/static | The reusable DAT 0.9.0 Display starter type-checked against the actual `MWDATCore` and `MWDATDisplay` simulator XCFramework interfaces; this did not modify the sibling project or prove runtime Display behavior. |
| `PRE-ARCHIVE-01` | not-run | No signed archive, entitlement inspection, release channel, or production claim. |
| `DAT-REG-01` / `DAT-SES-01` | not-run | Registration, callback, session, disconnect, and recreation need a named connected pair. |
| `DAT-DISP-01` / `DAT-CAM-01` / `DAT-AUD-01` | not-run | Display, camera, and audio behavior need the named physical script. |
| `INP-PHYSICAL-01` | not-run | Physical Display/button/input behavior is not established. |
| `ODC-PHYS-01` | not-run | Static phone-local classification is not physical on-device proof. |

## Next gate

1. Preserve enough free disk for repeated target and simulator runs without deleting project sources.
2. Capture the named phone/Meta AI/on-glasses DAT-app/firmware/runtime/channel tuple.
3. Run connected registration/session/capability tasks against the selected target.
4. Execute the physical Display/camera/audio/input/disconnect/doff/fallback script.
5. If a Web App route is requested, add the Meta metadata contract and verify a public HTTPS origin before browser-simulator or physical Display work.

Do not generalize this iOS target to Android, all Gen 2 variants, or Gen 3.
The Android route remains source-covered but has no target in this sibling; Gen
3 remains unresolved until official mapping and named-device evidence exist.

## Sources

- [Tiny Detour implementation handoff](target-intakes/tiny-detour-ios-implementation-handoff.yaml)
- [Target preflight reference](../skills/packages/meta-wearables-device-proof/references/target-preflight.md)
- [Redacted iOS target receipt runner](../skills/packages/meta-wearables-device-proof/scripts/run_ios_target_preflight.py)
- [Web App preflight receipt runner](../skills/packages/meta-wearables-web-apps/scripts/run_webapp_preflight.py)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [Implementation recipes and build handoffs](29-implementation-recipes-and-build-handoffs.md)
- [Completion audit and next proof](32-completion-audit-and-next-proof.md)
