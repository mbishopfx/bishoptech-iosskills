# Meta Wearables implementation recipes and build handoffs

This route turns a selected Meta Wearables API row and vertical-slice playbook
into a source-aligned implementation skeleton for iOS DAT, Android DAT, native
Display, Ray-Ban Display Web Apps, or a shared outcome with a phone fallback.

The detailed portable reference is the [implementation-recipes skill](../skills/packages/meta-wearables-implementation-recipes/SKILL.md), its [recipe reference](../skills/packages/meta-wearables-implementation-recipes/references/implementation-recipes.md), and the [implementation-handoff template](../skills/packages/meta-wearables-implementation-recipes/references/implementation-handoff-template.yaml). Load the [source-pinned API register](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml) and one [vertical-slice playbook](28-reference-implementation-playbooks.md) first.

The current cross-platform first-slice packet is the [shared-glance handoff](target-intakes/meta-wearables-shared-glance-cross-platform-handoff.yaml).
It is deliberately a draft: it proves that the iOS, Android, Web App, shared
state, phone fallback, and evidence lanes can be routed together, not that one
target or named pair has passed them all.

## Recipe lanes

| Lane | Source-aligned shape | Required rows | Compile/runtime boundary |
| --- | --- | --- | --- |
| iOS DAT camera | `DeviceSession` → [DAT 0.9 camera starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-camera-starter/MetaWearablesCameraStarter.swift) → bounded consumer/photo sink → phone result | `IOS-CORE-001`, `IOS-REG-001`, `IOS-PERM-001`, `IOS-DEVICE-001`, `IOS-SESSION-001`, `IOS-CAMERA-001`, `IOS-MEDIA-001` | Compile against the pinned SPM products; stop camera children before the session and keep raw frames out of shared state. |
| iOS native Display | runtime `supportsDisplay()` → [DAT 0.9 Display starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-display-starter/MetaWearablesDisplayStarter.swift) → sanitized content/action → phone fallback | `IOS-DEVICE-001`, `IOS-SESSION-001`, `IOS-DISPLAY-001`, `GEN-PHYSICAL-01` | Source-aligned to the pinned DAT 0.9.0 iOS shapes; a compile, source symbol, or mock does not prove a named pair can render or accept input. |
| Android DAT camera | `DeviceSession` → [DAT 0.9 camera starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-camera-starter/MetaWearablesAndroidCameraStarter.kt) → `Camera.stream` → bounded `Flow` consumer/photo sink | `AND-CORE-001`, `AND-DEVICE-001`, `AND-SESSION-001`, `AND-CAMERA-001` | Resolve Maven artifacts, `DatResult`, coroutine, Manifest, min/compile SDK, and R8 behavior; the source-aligned asset is not a target compile receipt. |
| Android native Display | capability gate → [DAT 0.9 Android Display starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-display-starter/MetaWearablesAndroidDisplayStarter.kt) → `sendContent { ... }` builder → tap/click event → `removeDisplay()` → session stop | `AND-SESSION-001`, `AND-DISPLAY-001`, `AND-DEVICE-001`, `AND-PHYS-01` | Source-aligned to the official Android 0.9.0 DisplayAccess sample; compile against the selected Maven artifact and keep target/physical proof separate. |
| Android target bootstrap | [Credential-safe DAT target starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md) → permission/init shell → selected capability adapter | `AND-CORE-001`, `AND-CONFIG-01`, `AND-BUILD-01` | Pins the official 0.9.0 Android build graph and private credential path; it is not a compile, connected, physical, Gen 2/Gen 3, signed, or release receipt. |
| iOS/Android MockDevice fixtures | [iOS MockDevice starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift) or [Android MockDevice starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt) → enable/pair → lifecycle/permission/media/input fixture → sanitized adapter assertions → unpair/disable | `IOS-MOCK-001`, `AND-MOCK-001`, `ODC-MOCK-01`, `ARCH-MOCK-01` | iOS fixture type-checks against DAT 0.9.0; Android remains compile-open; either result is mock evidence only and cannot replace physical radio/optics/audio/firmware/input proof. |
| iOS XCUITest MockDevice control | [iOS MockDevice test-client starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-test-client-starter/MetaWearablesMockDeviceTestClientStarter.swift) → app-process test server → UI-test-process `MockDeviceTestClient` → sanitized lifecycle/captouch/media assertions → teardown | `IOS-MOCK-001`, `ODC-MOCK-01`, `ARCH-MOCK-01` | Type-checks against the test-only DAT 0.9.0 product; the process boundary and local-network/port setup remain target-owned, and the result is mock evidence only. |
| Ray-Ban Display Web App | HTTPS revision → 600×600 focused DOM → host/input/exit handling → phone fallback | `WEB-RUNTIME-001`, `WEB-INPUT-001`, `WEB-SIM-001`, `WEB-NET-001`, `WEB-PHYSICAL-001` | Browser simulation and hosted launch do not prove physical Display optics, input, or release behavior. |

## Non-negotiable handoff fields

Every generated recipe must state:

- one outcome, primary surface, and useful phone fallback;
- exact app/OS/package or artifact/hosted revision/runtime/phone/companion/
  firmware/channel tuple, with unknowns marked `to-verify`;
- selected manifest API rows and evidence IDs;
- confirmed versus unresolved imports and method signatures;
- one coordinator, one capability owner, one session epoch, and child-before-
  parent stop order;
- bounded media/audio/sensor processing, retention/deletion, network, consent,
  thermal, background, doff/disconnect, and stale-event behavior;
- reducer/fake/MockDevice/browser/build/connected/physical cases and the next
  proof task.

Validate the packet before writing target code:

```sh
python3 ../skills/packages/meta-wearables-implementation-recipes/scripts/validate_implementation_handoff.py \
  <packet> \
  --manifest ../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml \
  --plan ../skills/packages/meta-wearables-full-sdk-audit/references/capability-evidence-plan.yaml \
  --team-manifest ../skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml
```

The bundled template is allowed to contain placeholders; a real
`ready-for-implementation` packet is not.

## Shared-domain starter

The portable [shared-domain starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-domain-starter/)
is a small Swift package for typed product state, registration/permission
gates, capability epochs, stale-event rejection, child-before-parent teardown,
and phone fallback. It intentionally contains no MWDAT, Kotlin, browser, media,
or device objects.

Run its deterministic Swift Testing suite before adapting it into a sibling
project:

```sh
swift test --package-path ../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-domain-starter
```

Passing this package proves only the shared reducer contract. The selected DAT
SPM product, Android artifact, Web App revision, target build, and named-device
behavior remain separate gates.

## Android target starter

When no Android Gradle target exists, copy the [portable DAT target starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md)
into a new sibling project before adding a capability adapter. It mirrors the
official DisplayAccess build graph at AGP `8.11.1`, Kotlin `2.2.21`, Gradle
`8.14.1`, SDK `36/31`, Java/Kotlin `17`, and DAT artifacts `0.9.0`. The starter
keeps GitHub Packages and Developer Center values in environment variables or
ignored `local.properties`; no credential value belongs in the skill archive.

Run `gradle :app:assembleDebug` only from a copied target with Android SDK 36,
Java 17, and authenticated artifact access. The current knowledge-base host has
none of those Android build prerequisites, so this starter is intentionally
compile-open until a real target-preflight receipt exists.

## Ray-Ban Display Web App starter

The portable [Web App starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-web-starter/)
provides a dependency-free 600×600 high-contrast HTML shell, visible focus,
keyboard-equivalent input, bounded text projection, stale-event rejection,
network/timeout/error states, host exit, and a phone fallback. Its reducer is
independent of the moving Web App toolkit and intentionally does not invent a
host global.

Run its deterministic Node suite from the knowledge-base directory:

```sh
node --test ../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-web-starter/test/display-state.test.mjs
```

Run the strict local Web App preflight as well:

```sh
python3 ../skills/packages/meta-wearables-web-apps/scripts/run_webapp_preflight.py \
  ../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-web-starter \
  --require-meta-markers --node-check
```

The current starter receipt is `status=pass`, `evidence_level=static`, with
the MRBD metadata markers, 600×600 viewport, local script, package manifest,
and Node syntax check passing. Its next gate is a public HTTPS origin and the
official browser simulator. Resolve the selected toolkit revision and host
input/exit contract, deploy the public revision, and then repeat the same
script on a named physical Ray-Ban Display pair. None of those gates can be
replaced by the Node suite, the local preflight, or a desktop browser.

## MockDevice fixture starters

Use the [iOS MockDevice starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-ios-mockdevice-starter/MetaWearablesMockDeviceStarter.swift)
or [Android MockDevice starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-mockdevice-starter/MetaWearablesAndroidMockDeviceStarter.kt)
after the target owns the matching DAT MockDevice product/artifact. Exercise
permission denial and request outcomes, pairing, power/fold/don/doff, camera
feed/photo fixtures, captouch, stale/cancelled adapter work, and child-before-
parent teardown. Assert sanitized state or counts only; keep URIs, media,
identifiers, and credentials out of logs and archives. The iOS starter has a
DAT 0.9.0 simulator typecheck receipt; the Android starter remains compile-open
until a Maven-backed target exists.

## Source and evidence boundaries

- The iOS and Android 0.9 changelogs establish the consolidated Camera route;
  they do not establish the exact generated signature in an arbitrary target.
- Native DAT, native Display, Web Apps, and phone fallback remain separate
  adapters. Shared domain code receives typed product events, not SDK objects.
- `Gen 2`, `Gen 2 Optics`, `Meta Glasses`, and user-provided `Gen 3` wording do
  not substitute for runtime `DeviceType`, capability response, firmware, and
  physical evidence. The public mapping for “Gen 3” remains `to-verify`.
- “On-device” requires a processing-location declaration. Phone-local camera
  processing is not glasses-native computation; HFP, A2DP, phone microphone,
  browser sensors, and remote services are different data paths.
- Compile, MockDevice, browser-simulator, hosted URL, Developer Mode,
  attestation, or signed-release results cannot be reported as physical glasses
  or production proof.

## Sources

- [Portable implementation recipes skill](../skills/packages/meta-wearables-implementation-recipes/SKILL.md)
- [Implementation recipe reference](../skills/packages/meta-wearables-implementation-recipes/references/implementation-recipes.md)
- [Source-pinned API register](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
- [Vertical-slice playbooks](28-reference-implementation-playbooks.md)
- [Application architecture and platform boundaries](19-application-architecture-and-platform-boundaries.md)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md)
- [DAT Android DisplayAccess sample](https://github.com/facebook/meta-wearables-dat-android/tree/main/samples/DisplayAccess)
- [Meta Wearables Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
