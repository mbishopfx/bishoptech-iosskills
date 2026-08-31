# Developer operations contract

Use this contract for a source, account, configuration, distribution, telemetry,
or recovery packet. It records what the Developer Center journey establishes and
what still requires authenticated account or target evidence.

## Required identity tuple

```text
company: <redacted or named only when safe>
mma_organization: <known | missing | access-gated | not-run>
wearables_team: <known | missing | access-gated | not-run>
operator_role: <admin | developer | tester | unknown>
project: <redacted name or not-run>
platform_app: <ios bundle id / android package name / web URL, redacted as needed>
target_build_or_url: <version/build/URL or not-run>
integration_version: <major.minor.patch or not-run>
release_channel: <developer mode / invite-only name / production / not-run>
tester_meta_account: <accepted | invited | declined | removed | unknown | not-run>
companion_firmware_tuple: <known values or not-run>
evidence_level: <source | access-gated | account | static | build | physical | signed | release-channel>
```

## Evidence IDs

| ID | Required observation | Evidence level | Does not prove |
| --- | --- | --- | --- |
| `DCO-SOURCE-01` | Re-open official operations/reference pages and record retrieval date/revision. | `source` | account access or current UI state |
| `DCO-ORG-01` | Resolve one-company MMA organization, team membership, and operator role. | `account` | project configuration or tester acceptance |
| `DCO-PROJECT-01` | Inspect project, platform app identity, product listing, permissions, and callback/build config. | `account`/`static` | target compile or physical registration |
| `DCO-VERSION-01` | Inspect a version and record Major/Minor/Patch intent plus DAT build status. | `account`/`release` | channel tester access or device behavior |
| `DCO-CHANNEL-01` | Inspect channel, selected version, invite mode, tester list, and account acceptance. | `account`/`release-channel` | physical capability or production approval |
| `DCO-TESTER-01` | Confirm tester Meta Account acceptance and Meta AI app channel/permission state. | `account`/`connected` | camera, audio, Display, or firmware success |
| `DCO-TELEMETRY-01` | Record telemetry categories, opt-out metadata, product disclosure, retention, and deletion policy. | `static`/`release` | blanket privacy compliance |
| `DCO-RECOVERY-01` | Record a bounded build/channel/project recovery action and post-action state. | `account`/`release-channel` | a retry or documentation instruction without observation |

## Minimum fixture

Input: “Prepare one iOS and one Android DAT app for a private Ray-Ban Display
test channel, keep Developer Mode available, explain telemetry, and invite one
tester without leaking credentials.”

Expected output:

- verify or mark access-gated the existing MMA organization and Wearables team;
- create separate platform-app rows when iOS and Android identifiers differ;
- record product icon/name, camera/microphone/voice permission justifications,
  app ID/client-token mode, and privacy owner without storing values;
- assign a Major/Minor/Patch rationale and wait for the generated DAT application
  build to be `Ready` before channel distribution;
- distinguish the tester’s Meta Account from MMA membership and record invite
  acceptance separately from Meta AI app channel/permission state;
- preserve Developer Mode as a local-development path, not release evidence;
- document telemetry categories and opt-out metadata while separately auditing
  retention, deletion, disclosure, and user consent;
- return all eight `DCO-*` rows with `not-run`, `access-gated`, or observed
  receipts, plus the physical DAT/Display task still required.

## Destructive-operation stop

Project deletion, member removal, tester revocation, channel switching, restore,
and release publication are state-changing operations. Resolve the exact target,
confirm the user’s authorization, capture a pre-action receipt, and record the
post-action state. A source page or stale screenshot is not sufficient.

## Sources

- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Onboarding and organization management](https://wearables.developer.meta.com/docs/onboarding-and-organization-management)
- [Manage projects](https://wearables.developer.meta.com/docs/manage-projects)
- [Set up release channels](https://wearables.developer.meta.com/docs/set-up-release-channels)
