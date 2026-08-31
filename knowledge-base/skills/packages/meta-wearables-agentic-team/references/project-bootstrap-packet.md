# Meta Wearables project bootstrap packet

Use this packet when the current workspace has no concrete Xcode target,
Gradle project, or hosted Web App. It turns the product request into a bounded
project handoff without treating the knowledge-base repository as the app.

## Start outside the knowledge-base repo

Create the implementation in a new sibling project folder. Keep the shared
planning and evidence packet beside the platform targets, not inside the
portable skill package. Do not copy secrets, raw camera/audio, device IDs, or
private Developer Center payloads into the packet.

First run the team preflight against the candidate workspace:

```sh
python3 scripts/run_team_preflight.py <workspace-root> --json
```

Carry the `decision`, check statuses, target-surface `overall`,
`configured_surfaces`, `partial_surfaces`, and `bootstrap_required` fields into
the handoff. A structural signal or green manifest check never proves that a
target builds or that a device supports a capability.

## Intake

Fill every unknown as `to-verify`; do not infer a product, SDK, or generation
from a consumer label.

```yaml
project_slug: <stable-project-name>
parent_folder: <sibling-folder>
outcome: <one user-visible outcome>
primary_surface: native-dat-ios | native-dat-android | native-display | web-app | phone-fallback
secondary_surfaces: []
platform_targets:
  ios:
    target: <xcode target or to-verify>
    deployment_target: <value or to-verify>
    dat_product: <exact MWDAT product or to-verify>
    package_revision: <SPM revision/tag or to-verify>
  android:
    module: <Gradle module or to-verify>
    artifact: <exact Maven artifact/version or to-verify>
  web:
    hosted_revision: <commit/URL or to-verify>
device_claims:
  - label: ray-ban-display | gen-2 | gen-3 | other
    runtime_identity: <exact runtime/model or to-verify>
    capability: <supportsDisplay/camera/audio/input/etc. or to-verify>
    firmware: <version or to-verify>
companion_and_channel:
  meta_ai_version: <value or to-verify>
  on_glasses_dat_app: <value or to-verify>
  mode: developer | release | to-verify
  channel: <value or to-verify>
data_path:
  processing_location: glasses | phone | browser | remote | mixed | to-verify
  camera_audio_sensor_inputs: []
  retention_deletion: <policy or to-verify>
fallback: <useful phone behavior when wearable path is absent>
requested_proof: static | mock | build | connected | physical | signed | release
open_gates: []
```

## Select the first vertical slice

Choose one outcome before delegating the whole SDK:

- **Native Display:** capability predicate → minimal card/button surface →
  action result → clear/replace → phone fallback.
- **Camera to phone:** permission/consent → one session owner → bounded camera
  stream or photo → phone-local result → deterministic teardown.
- **Web App Display:** public HTTPS revision → focused 600×600 surface → host
  input/exit handling → phone fallback.
- **Phone fallback:** the useful product outcome still works when registration,
  pairing, capability, permission, transport, or hardware proof is absent.

The selected slice must list its manifest API rows, capability/evidence-plan
IDs, owner roles, privacy path, unresolved signatures, and next proof task.

## Project layout and evidence ladder

Prefer separate adapters over a cross-platform SDK-shaped abstraction:

```text
<sibling-project>/
  docs/meta-wearables/target-intake.yaml
  apple/                 # native DAT iOS and phone fallback when selected
  android/               # native DAT Android when selected
  web/                   # Display Web App when selected
  shared/                # typed product state/policy only, if useful
```

For an Android-first bootstrap, the implementation-recipes package includes a
[credential-safe DAT target starter](../../meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md).
Copy it into the new sibling's `android/` folder, replace the example
namespace/application ID, and keep `local.properties`, Developer Center
values, GitHub Packages access, signing, and device identifiers outside the
knowledge base. It is only a target-owned permission/init shell; the selected
capability recipe and target-preflight receipt still have to follow it.

Run the evidence ladder in order: static source/API resolution, MockDevice or
browser simulation, target build, connected-device run, named physical-device
run, signed artifact, and release-channel check. A higher-level result does not
erase a lower-level failure, and a compile/mock/simulator result never proves
glasses behavior.

## Required bootstrap handoff

Return the selected route, exact package/artifact/hosted revision, target tuple,
state owner and stop order, processing-location/privacy contract, fallback,
selected API/evidence IDs, test seams, current evidence level, and the next
proof task. Keep `Gen 3` and “regular SDK” unresolved until an official source,
selected runtime, artifact/API, and named-device result establish their meaning.
