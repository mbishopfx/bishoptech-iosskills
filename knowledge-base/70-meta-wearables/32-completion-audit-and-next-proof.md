# Meta Wearables completion audit and next proof

This is the living status route for the Meta Wearables objective. It prevents
the knowledge base, a green validator, or a portable skill archive from being
reported as an implemented or physically verified app.

Run the consolidated [team preflight](../skills/packages/meta-wearables-agentic-team/scripts/run_team_preflight.py)
before changing a status. The current snapshot is based on the pinned public
source set reviewed on 2026-08-22.

## Requirement audit

| Objective requirement | Current evidence | Status | What still closes it |
| --- | --- | --- | --- |
| Advanced Meta Wearables knowledge base | 34-route [knowledge-base index](README.md), source registry, API atlases, capability/evidence plan, privacy, transport, debugging, operations, architecture, recipes, target intake, release routes, and machine-checked upstream AI surfaces | covered | Keep the source snapshot refreshed when official repositories or the full reference drift. |
| Full public DAT surface | [Surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml) revision 4 with 30 API rows, 14 capabilities, 47 evidence tasks, four journeys, five iOS products, four Android artifacts, and a 23-check source-tree receipt | source-verified | Resolve selected package/artifact symbols in a real target and run the relevant build/device rows. |
| Native iOS and Android skill coverage | 23 local roles, 32 exact upstream plugin-role handoffs, dedicated iOS/Android API-atlas packages, compile-tested iOS Display, camera, MockDevice, and test-client seeds, source-aligned Android Display, camera, and MockDevice seeds, a credential-safe Android DAT 0.9 target starter, and a redacted Android target-preflight runner exercised against that starter | source-verified | Compile the Android camera/Display/MockDevice routes in a real Maven-backed target, then capture connected-device, physical, signed, and release evidence for camera, Display, audio, and input. |
| “Regular SDK” route | Current public materials are routed as native DAT or hosted Web Apps; the team does not invent a third public native SDK | terminology-resolved | Name the intended surface in each project request. |
| Ray-Ban Display apps | Native Display and hosted Web App routes, Display capability gates, 600×600 guidance, input/fallback/privacy contracts | source-and-static | Complete `DAT-DISP-01` and/or `WEB-PHYS-01` on a named Display pair and repeat the signed route. |
| Regular Gen 2 support | Gen 2 terminology, compatibility tuple, runtime capability, firmware, companion, and physical evidence tasks | source-routed, not physically proven | Complete `COMP-TUPLE-01`, `COMP-CAPABILITY-01`, and `COMP-RELEASE-01` on the exact named pair. |
| Gen 3 support | Current public source snapshot does not establish a Gen 3 mapping; the team keeps the alias `to-verify` and blocks enum/product-name inference | open | Obtain official mapping, observed runtime identity, exact firmware/companion tuple, and repeated named-device operation. |
| On-device compliance | Processing-location, consent, retention/deletion, network, thermal, lifecycle, and fallback contracts across the KB and specialist roles | contract-covered | Verify the declared data path in the selected target and physical run; phone-local or remote processing must not be called glasses-native. |
| Agent skill team | [Team manifest](../skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml), 23 roles, 32 handoffs, claim gates, root AI-surface inventory, preflight runner, bootstrap packet, evidence contract, and machine-checked compatibility packet | packaged | Use the team on a concrete project and preserve its validated compatibility, target, and physical receipts in the handoff. |
| Portable skill delivery | 42 package directories match 42 `.skill` archives; team and device-proof archives include their scanners/preflight resources | packaged-and-qa-verified | Repackage after any source or workflow change. |
| Actual iOS/Android/Web implementation | The knowledge-base root remains target-free, but the existing `bishoptech-sidequest` sibling has an iOS target plus a generic local web surface; that sibling Web App remains not-ready because Meta markers and hosted HTTPS delivery are absent. Separately, the portable Web App starter now passes strict metadata, local-asset, package, and Node syntax preflight at static evidence level. The redacted iOS handoff validates, the portable iOS target receipt runner passes target/settings inspection, 65 simulator tests pass against DAT 0.9.0, and the reusable native iOS Display, camera, MockDevice, and test-client starters type-check against the same DAT 0.9.0 Core/Display/Camera/MockDevice/MockDeviceTestClient XCFramework interfaces. The Android lane now has portable Gradle/Maven target, Display, camera, and MockDevice starters plus a static redacted target-preflight receipt; none are compiled here because no Android SDK/Gradle/Maven-auth path is present. The new [shared-glance cross-platform handoff](target-intakes/meta-wearables-shared-glance-cross-platform-handoff.yaml) validates 21 API rows, 17 evidence tasks, and 14 owner roles across the native, Web App, shared-state, and phone-fallback lanes. | iOS target and reusable iOS Display/camera/MockDevice/test-client recipe compile/build/test boundaries recorded; Android target/recipes compile-open; portable Web App static preflight pass; cross-platform draft handoff validated; hosted/simulator/physical Web App proof open | Create the sibling project named by the shared-glance packet, choose the first primary surface, capture target preflight and compile receipts, then advance through connected and named physical Display/camera/audio/input evidence. For Web Apps, add a public HTTPS origin, run the official browser simulator, then execute the named physical Display script. |
| Developer Center, signed, and release proof | Routes and checklists exist, but no authenticated project/channel or signed artifact is present in this workspace | not run | Use authorized account state and the exact target/build/channel; keep credentials and private identifiers redacted. |

## Evidence boundary

The strongest current result is a source/manifest/team result plus a static
target-intake and simulator build/test result, not connected or physical
hardware evidence. The knowledge-base root preflight still reports `NO_TARGET`;
when pointed at the existing sibling target, the structural scan reports
`TARGETS_PRESENT`, the implementation handoff validates, Xcode target/settings
inspection passes, and the test suite passes on the iOS 26.4 simulator. The
current live combined run passes the source-tree and source-revision checks; an
earlier retry during target diagnosis recorded a transient GitHub API rate-limit
failure, which is now superseded by the current `23/0` receipt:

```text
knowledge-base-root: decision=bootstrap target=NO_TARGET
selected-sibling: target=TARGETS_PRESENT handoff=pass iOS-receipt=pass build/test=65-pass
source receipts: CHECKS 5 DRIFT 0 and CHECKS 23 DRIFT 0; live team decision=target-preflight
```

That is the correct result for the knowledge-base repository. The selected
sibling has passed static target preflight and simulator build/test; this does
not promote the result to connected, physical, account, signed, or release
evidence. The separate native Display starter compile gate confirms only that
the reusable adapter resolves against DAT 0.9.0 Core/Display interfaces; it is
not a physical rendering or input result.

The current official route anchors are the [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios),
[DAT Android repository](https://github.com/facebook/meta-wearables-dat-android),
[DAT Android DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess),
[Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp),
and [full DAT reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat).

## Next proof packet

For the first implementation pass, use the selected Tiny Detour sibling or a
new isolated project and return one completed packet containing:

1. one outcome and first slice: native Display, camera-to-phone, audio-first,
   Web App Display, or phone fallback;
2. the team-preflight JSON receipt and exact target root;
3. iOS target/SPM product, Android module/Maven artifact, or hosted Web App
   revision;
4. product/SKU, observed runtime identity, phone OS, Meta AI version,
   on-glasses DAT-app version, firmware, mode, channel, and capability result;
5. processing-location, consent, retention, network, thermal, cancellation,
   stale-event, and fallback behavior;
6. selected API rows, capability/evidence-plan IDs, role owners, and open gates;
7. evidence in order: static, mock/browser-sim, build, connected, physical,
   signed, and release-channel.

The current packets are [Tiny Detour’s redacted iOS implementation handoff](target-intakes/tiny-detour-ios-implementation-handoff.yaml)
and the [shared-glance cross-platform draft handoff](target-intakes/meta-wearables-shared-glance-cross-platform-handoff.yaml),
with the [target-intake receipt](33-existing-target-intake-and-preflight.md).
They remain pre-connected and pre-physical.

Do not close the overall objective until the open rows above have authoritative
evidence. In particular, Gen 2 physical support, Ray-Ban Display behavior,
“on-device” processing location, and any Gen 3 mapping are separate claims.

## Related routes

- [Meta Wearables knowledge base](README.md)
- [Agent team roster and handoff contract](30-agent-team-roster-and-handoff-contract.md)
- [Project bootstrap and target intake](31-project-bootstrap-and-target-intake.md)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [Device-generation and runtime-support matrix](16-device-generation-and-runtime-support-matrix.md)
- [On-device compliance and runtime contract](17-on-device-compliance-and-runtime-contract.md)
