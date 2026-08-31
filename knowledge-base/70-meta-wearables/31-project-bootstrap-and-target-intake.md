# Project bootstrap and target intake

The Meta Wearables lane is a knowledge base and portable skill team; it is not
an app target. When a request arrives before an Xcode project, Gradle module,
or hosted Web App exists, use the portable [project bootstrap packet](../skills/packages/meta-wearables-agentic-team/references/project-bootstrap-packet.md)
to create a clean implementation handoff in a new sibling project folder.

Start by running the bundled [team preflight runner](../skills/packages/meta-wearables-agentic-team/scripts/run_team_preflight.py)
against the knowledge-base root and, when the app is a sibling, pass that app
root with `--target-root`. Its decision receipt combines structural,
manifest, capability-plan, and optional live-source checks; neither a green
receipt nor a structural target signal is a build or hardware claim.

## Why this route exists

The SDK surface crosses native iOS or Android code, the Meta AI companion,
wearable firmware, an on-glasses DAT app, transport, and (for Display Web
Apps) a hosted HTTPS surface. A project packet freezes those boundaries before
any code or device claim is made.

The packet is also the place to resolve the user’s “regular SDK” wording. The
current public routes are native DAT and Display Web Apps; the team must name
the selected route rather than invent a third SDK. “Gen 3” remains
`to-verify` until official mapping and named-device evidence exist.

## Bootstrap sequence

1. Create a sibling project folder and record one outcome, primary surface, and
   useful phone fallback.
2. Freeze the exact iOS SPM product, Android Maven artifact, or Web App hosted
   revision. Unknowns remain `to-verify`.
3. Fill the device, runtime, capability, phone, companion, firmware, DAT-app,
   mode, channel, privacy, and processing-location tuple.
4. Select one vertical slice: native Display, camera-to-phone, Web App Display,
   or phone fallback. Do not start with an undifferentiated “full SDK” build.
5. Route the slice through the 23-role [agent team](../skills/packages/meta-wearables-agentic-team/SKILL.md),
   carrying manifest API rows, capability/evidence-plan IDs, owner roles, and
   open gates.
6. Promote evidence only in order: static, mock/simulator, build, connected,
   named physical device, signed artifact, and release channel.

The current source-validated first cross-platform packet is the [shared-glance
handoff](target-intakes/meta-wearables-shared-glance-cross-platform-handoff.yaml).
It binds the iOS DAT Display, Android DAT Display, Ray-Ban Display Web App, and
phone-fallback adapters to one outcome while retaining separate API, privacy,
processing-location, target, and physical-proof gates. It is a draft recipe
packet, not an app target or a device-support claim.

## Starter project shape

```text
<sibling-project>/
  docs/meta-wearables/target-intake.yaml
  apple/                 # selected iOS DAT and phone route
  android/               # selected Android DAT route
  web/                   # selected Display Web App route
  shared/                # typed product state/policy only, if useful
```

For the Android lane, the portable [DAT target starter](../skills/packages/meta-wearables-implementation-recipes/assets/meta-wearables-android-target-starter/README.md)
provides the source-observed 0.9.0 Gradle/Maven shell and a target-owned
permission/init screen. Copy it into the new sibling only after selecting the
first slice; keep `local.properties`, environment credentials, signing, and
device identifiers out of this knowledge-base repository.

Once a real Android sibling exists, run the redacted [Android target-preflight
runner](../skills/packages/meta-wearables-device-proof/scripts/run_android_target_preflight.py)
against its Gradle root before dependency or build work. It records the
module/variant, DAT coordinates, SDK/toolchain signals, Manifest inputs, and
credential presence without exposing values; a static pass still needs the
selected Maven graph and variant compile before any device claim.

Keep SDK objects at platform boundaries. Shared code should receive typed
product events and policy decisions; it must not assume that iOS symbols,
Android artifacts, native Display, and Web Apps have identical capabilities.

## Sources and handoff

- [Portable project bootstrap packet](../skills/packages/meta-wearables-agentic-team/references/project-bootstrap-packet.md)
- [Agent team roster and handoff contract](30-agent-team-roster-and-handoff-contract.md)
- [Reference implementation playbooks](28-reference-implementation-playbooks.md)
- [Implementation recipes and build handoffs](29-implementation-recipes-and-build-handoffs.md)
- [Device and release evidence packet](12-device-and-release-evidence-packet.md)
- [Application architecture and platform boundaries](19-application-architecture-and-platform-boundaries.md)
