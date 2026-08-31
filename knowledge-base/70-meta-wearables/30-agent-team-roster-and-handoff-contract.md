# Meta Wearables agent team roster and handoff contract

This page is the human-readable entry point for the machine-readable [team
manifest](../skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml).
It turns the Meta Wearables knowledge base into a repeatable team: every
upstream plugin role has a local owner, every implementation route has a hard
gate, and every device-generation claim has a named evidence requirement.

## Team shape

| Layer | Local roles | Responsibility |
| --- | --- | --- |
| Route and coverage | `meta-wearables-route-planner`, `meta-wearables-full-sdk-audit`, `meta-wearables-agentic-team` | Resolve DAT iOS, DAT Android, Web Apps, phone fallback, terminology, upstream role coverage, source conflicts, and the final handoff. |
| Native DAT | `meta-dat-ios-integration`, `meta-dat-api-atlas`, `meta-dat-camera-audio`, `meta-dat-display`, `meta-dat-android-integration`, `meta-dat-android-api-atlas` | Own selected package/artifact, registration, session, camera/audio, Display, Android parity, exact symbols, and compile gates. |
| Web Apps and architecture | `meta-wearables-web-apps`, `meta-wearables-app-architecture`, `meta-wearables-input-sensors`, `meta-wearables-implementation-recipes` | Own the hosted 600×600 route, shared state and adapters, input/sensors, scaffolding, fallbacks, and test seams. |
| Compliance and reliability | `meta-wearables-on-device-compliance`, `meta-wearables-privacy-publishing`, `meta-wearables-transport-reliability`, `meta-wearables-operational-readiness` | Own processing location, consent, retention, network/audio/thermal behavior, recovery, privacy, terms, and release boundaries. |
| Operations and proof | `meta-wearables-developer-operations`, `meta-wearables-security-attestation`, `meta-wearables-debugging-observability`, `meta-wearables-device-compatibility`, `meta-wearables-device-proof`, `meta-wearables-source-refresh` | Own account/channel state, identity and callbacks, read-only diagnosis, model/version tuples, evidence levels, source drift, and physical proof. |

## Upstream coverage

The manifest pins all 10 DAT iOS roles, all 10 DAT Android roles, and all 12
Web Apps roles. The live source-tree checker verifies the names; the team
validator verifies that each one has a local handoff owner. Role-name similarity
is routing evidence only and never establishes cross-platform API parity.

## Required handoff

Every non-trivial request must carry:

- outcome and consequence of failure;
- selected surface and rejected alternatives;
- source/package/artifact revision and exact target tuple;
- selected local roles and upstream handoff IDs;
- implementation boundary, data/processing-location contract, consent,
  retention, thermal/lifecycle behavior, and typed fallback;
- preflight, mock/browser, build, connected, physical, signed, and release
  evidence kept as separate levels;
- open account, firmware, companion, device, policy, and release gates;
- next proof task.

Use the portable [routing receipt runner](../skills/packages/meta-wearables-agentic-team/scripts/route_capability.py)
to make that selection repeatable:

```sh
python3 ../skills/packages/meta-wearables-agentic-team/scripts/route_capability.py \
  --capability native-display \
  --workspace-root . \
  --json
```

For the composite request, replace `--capability native-display` with
`--full-sdk`. The receipt selects the manifest capability rows, local owners,
upstream role handoffs, preflight tasks, required evidence levels, terminology
guardrails, source revision, processing boundary, and next action. It does not
claim that any selected role compiled, connected, rendered, or shipped.

“On-device” is a data-path claim, not a synonym for “runs on the glasses.”
Classify each path as `glasses-native`, `phone-local`, `remote`, `mixed`, or
`unknown`, and preserve the phone fallback when the wearable is absent or not
proven.

## Device claim gates

| Claim | Minimum closure |
| --- | --- |
| Ray-Ban Display | Named physical rendering/input task for native Display or Web Apps, with the exact URL/package, model, firmware, companion, and build recorded. |
| Gen 2 | Official/runtime tuple plus named-device capability run and release-critical rerun; do not generalize one SKU or firmware. |
| Gen 3 | Official current model mapping, observed runtime identity, firmware, and repeated named capability run. The current knowledge base keeps this `to-verify`. |

MockDevice, browser simulation, source lookup, registration, Developer Mode,
and a successful compile remain useful lower-level evidence but cannot close a
physical or release claim. See the [device and release evidence packet](12-device-and-release-evidence-packet.md).

## Sources and maintenance

- [Machine-readable team manifest](../skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml)
- [Team skill](../skills/packages/meta-wearables-agentic-team/SKILL.md)
- [Full-SDK audit](../skills/packages/meta-wearables-full-sdk-audit/SKILL.md)
- [Public plugin and skill matrix](13-public-plugin-and-skill-matrix.md)
- [Source-pinned surface manifest](27-source-pinned-surface-manifest.md)
- [Source refresh route](../skills/packages/meta-wearables-source-refresh/SKILL.md)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
