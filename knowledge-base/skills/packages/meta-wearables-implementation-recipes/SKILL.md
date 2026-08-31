---
name: meta-wearables-implementation-recipes
description: Turn a selected Meta Wearables API row and vertical-slice playbook into source-aligned Swift, Kotlin/Java, or Ray-Ban Display Web App implementation scaffolding with explicit compile, privacy, lifecycle, fallback, and physical-device gates. Use when building or reviewing a concrete iOS DAT, Android DAT, native Display, Web App, or cross-platform wearable feature after route selection.
---

# Meta Wearables implementation recipes

Use this role after route selection and the full-surface audit. It converts one
outcome into a narrow adapter implementation handoff; it does not flatten DAT,
native Display, Web Apps, and phone fallback into one fictional SDK.

## Read before acting

- Read the [source-pinned API manifest](../meta-wearables-full-sdk-audit/references/surface-manifest.yaml) and filter exact `IOS-*`, `AND-*`, `WEB-*`, compatibility, and evidence rows.
- Read the [vertical-slice playbooks](../meta-wearables-app-architecture/references/vertical-slice-playbooks.md) and choose one playbook before writing scaffolding.
- Read the [application architecture contract](../meta-wearables-app-architecture/references/architecture-contract.md) for ownership, epochs, cancellation, fallback, and test seams.
- Read the [iOS API atlas](../../../70-meta-wearables/10-dat-ios-api-surface-atlas.md) or [Android API atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md) for the selected target; read the [Web Apps route](../../../70-meta-wearables/06-web-apps-display-and-input.md) for hosted work.
- Load the selected capability entry from the [capability/evidence plan](../meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml) and preserve its owner roles, implementation route, privacy path, fallback, required evidence levels, and proof task IDs in the build handoff.
- Read the [on-device compliance contract](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md) before describing camera, audio, sensor, storage, or network processing.
- Inspect the actual target project, package graph, deployment/min SDK, privacy configuration, entitlements/manifest, and existing adapter before selecting a recipe.
- Read the [target-preflight reference](../meta-wearables-device-proof/references/target-preflight.md) when a concrete build, connected device, physical device, signed artifact, or release claim is in scope; carry its `PRE-*` status into the handoff.
- Create or update the [implementation-handoff packet](references/implementation-handoff-template.yaml) before scaffolding and run `python3 scripts/validate_implementation_handoff.py <packet> --manifest <surface-manifest> --plan <capability-plan> --team-manifest <team-manifest>`. Use `--allow-placeholders` only for the bundled template; a real ready packet must resolve its target tuple and `to-verify` fields.
- Use the [compile-tested shared-domain starter](assets/meta-wearables-domain-starter/) for typed product state, epoch handling, teardown ordering, and phone fallback. It deliberately has no DAT/Android/Web SDK imports; its passing tests prove shared reducer behavior only, never SDK compilation or hardware support.
- Use the [source-aligned iOS camera starter](assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift) for DAT 0.9 camera/photo work. It type-checks against the selected `MWDATCore`/`MWDATCamera` simulator frameworks, keeps raw frames inside the adapter, and makes the photo handoff, permission, stream, and child-before-parent teardown gates explicit.
- Use the [source-aligned Android camera starter](assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt) for DAT 0.9 Android camera/photo work. It follows the official `CameraAccess` `DatResult`/`Flow` shape, but remains an Android target compile gate until the selected Maven artifacts resolve.
- Use the [source-aligned iOS MockDevice starter](assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift) for deterministic iOS DAT fixtures. It type-checks against the selected DAT 0.9.0 `MWDATCore`/`MWDATMockDevice` interfaces and keeps mock lifecycle, permission, media, and captouch controls outside shared product state.
- Use the [source-aligned iOS MockDevice test-client starter](assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift) when XCUITest must control the app process's official MockDevice test server. It type-checks against the test-only `MWDATMockDeviceTestClient` product and keeps the app-process/server versus UI-test-process boundary explicit.
- Use the [source-aligned Android MockDevice starter](assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt) for deterministic Android DAT instrumentation fixtures. It follows the official 0.9.0 `MockDeviceKit` sample, but remains an Android target compile gate until the selected Maven artifacts resolve.
- Use the [source-aligned native iOS Display starter](assets/meta-wearables-ios-display-starter/MetaWearablesDisplayStarter.swift) when the selected vertical slice is native DAT Display. It targets the DAT 0.9.0 shapes resolved in the reference target: `supportsDisplay()`, `DeviceSession` state/error streams, `session.addDisplay()`, `Display.statePublisher`, `Display.send(FlexBox)`, and child-before-parent teardown. Type-check it against the selected SPM product before adapting it; the asset is not standalone proof of registration, physical rendering, or input behavior.
- Use the [source-aligned native Android Display starter](assets/meta-wearables-android-display-starter/MetaWearablesAndroidDisplayStarter.kt) when the selected vertical slice is native DAT Android Display. It follows the official 0.9.0 shape: `SpecificDeviceSelector`, `Wearables.createSession(...).fold`, `DeviceSession` `Flow` state/error collection, `addDisplay()`, `Display.state`, `sendContent`, `buttonGroup`, `removeDisplay()`, and parent-session stop. Resolve the exact Maven artifacts and compile it in the selected Android target; this knowledge base does not treat the uncompiled portable asset as target or hardware proof.
- When Android is selected but no Gradle target exists, copy the [credential-safe Android DAT target starter](assets/meta-wearables-android-target-starter/README.md) into a new sibling project. It pins the official 0.9.0 full-artifact DAT graph and GitHub Packages route, keeps Developer Center values outside the archive, and stops at a target-owned `Wearables.initialize(context)` bootstrap until the selected implementation handoff is ready.
- When the selected route includes a Ray-Ban Display Web App, copy or adapt the [dependency-free Web App starter](assets/meta-wearables-web-starter/). Its reducer tests prove bounded 600×600 state/input/fallback behavior only; the host toolkit contract, browser simulator, hosted URL, and physical Display run remain separate gates.
- Run `python3 scripts/validate_recipe_reference.py` after editing the bundled reference and before packaging; treat missing sections, unbalanced code fences, marker loss, or secret-like literals as blockers.

## Workflow

1. Create the implementation-handoff packet and validate its route, API rows,
   evidence tasks, owners, target tuple, lifecycle, privacy/data path, tests,
   fallback, and next proof task.
2. Freeze the outcome, primary surface, phone fallback, exact target tuple,
   package/artifact or hosted revision, requested proof level, and open gates.
3. Select one playbook and carry its API/evidence row IDs into the recipe.
4. Resolve the selected release’s generated API before writing imports or
   method signatures. Label any source-index-only or moving-reference name
   `to-verify`; use a clearly marked placeholder instead of inventing syntax.
5. Build the smallest adapter skeleton: registration/permission, device and
   capability gate, session/capability ownership, bounded data path, user
   projection, stop/cancellation, and typed fallback.
6. Keep shared product state free of MWDAT types, Kotlin classes, browser
   events, raw frames, raw audio, tokens, and device identifiers.
7. Run the shared-domain starter tests and, for a Web App route, the Web App
   starter Node tests. Then add deterministic reducer/fake/MockDevice/browser
   cases before requesting a
   target build. Record what each evidence level cannot prove.
8. If Android has no target, instantiate the target starter in a sibling folder,
   configure private values through ignored local properties or environment
   variables, and record the resulting `PRE-*` target receipt before adding
   capability code.
9. Return the implementation handoff, unresolved compile questions, privacy and
   retention decisions, exact next command/task, and the physical/release gate.

## Fast path

Freeze one playbook and target tuple; validate the handoff packet, select one starter, compile or type-check the adapter seam, and add only target-specific glue. Stop when a `to-verify` symbol or missing artifact blocks compile instead of hiding it behind placeholder code.

## Recipe selection

Load [implementation-recipes.md](references/implementation-recipes.md) only for
the selected surface. It contains source-aligned shapes for:

- iOS DAT 0.9 session/camera and native Display adapters;
- Android DAT 0.9 `DeviceSession`/`Camera`/Display builder boundaries;
- Ray-Ban Display Web App focus/input/host-exit handling; and
- one shared domain outcome with platform-specific adapters.

These are scaffolds, not claims that the user’s target compiles. The exact
package, generated API, OS, firmware, companion, and channel remain gates.
The Android target starter is a build-graph seed, not a DAT compile receipt;
its environment/local-properties credential path must remain outside source
control and archives.

## Hard boundaries

- Use the 0.9 consolidated `Camera` ownership path; do not generate removed
  `addStream` code from older examples.
- Keep iOS `AsyncSequence`/publisher, Android `Flow`/`DatResult`, and Web App
  browser events in their adapters; translate them to typed product events.
- Do not invent a native MWDATAudio module. Name phone microphone, HFP input,
  A2DP output, and remote processing separately.
- Do not map `Gen 3` or a product label to a runtime enum, Display support, or
  sensor capability without current official mapping and named-device evidence.
- A compile, mock, browser simulator, hosted URL, Developer Mode registration,
  or signed artifact is not physical glasses or production proof.
- Do not place client credentials, raw media, transcripts, serials, or private
  project data in example code, fixtures, logs, or handoffs.

## Required output

Return:

- selected playbook and normalized API/evidence row IDs;
- implementation-handoff packet path and validator receipt;
- shared-domain starter test command and result;
- exact target/package/artifact/hosted revision tuple and `to-verify` symbols;
- source-aligned adapter skeleton with explicit compile-gate comments;
- state owner, session epoch, resource stop order, cancellation, and fallback;
- processing location, consent, retention/deletion, network, and thermal path;
- reducer/fake/MockDevice/browser/build/connected/physical test cases;
- next proof task, unresolved questions, and source-refresh trigger.

## Related roles

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Full-SDK audit](../meta-wearables-full-sdk-audit/SKILL.md)
- [iOS DAT integration](../meta-dat-ios-integration/SKILL.md)
- [Android DAT integration](../meta-dat-android-integration/SKILL.md)
- [Web Apps](../meta-wearables-web-apps/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Implementation-handoff template](references/implementation-handoff-template.yaml)
- [Implementation-handoff validator](scripts/validate_implementation_handoff.py)

## Sources

- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Portable API manifest](../meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Vertical-slice playbooks](../meta-wearables-app-architecture/references/vertical-slice-playbooks.md)
