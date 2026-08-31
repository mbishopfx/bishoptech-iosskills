---
name: meta-wearables-developer-operations
description: Operate and audit the Meta Wearables Developer Center lifecycle for DAT iOS/Android and Ray-Ban Display Web Apps, including Managed Meta Account organization/team access, projects, platform app identities, product listings, permission justifications, versions, release channels, testers, Meta AI channel state, telemetry, and recovery. Use when onboarding a team, configuring a project, preparing a DAT release, diagnosing channel access, reviewing telemetry/privacy, or separating Developer Mode from signed distribution.
---

# Meta Wearables developer operations

Use this role for the account, project, configuration, distribution, and
telemetry layer around Meta Wearables integrations. It is not a substitute for
the DAT iOS/Android API roles, a physical-device run, or authorization to mutate
an external Developer Center account.

## Read before acting

- Read [the Developer Center operations route](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md), [the evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md), [privacy and publishing](../../../70-meta-wearables/08-privacy-publishing-and-release.md), and [operational readiness](../../../70-meta-wearables/18-operational-readiness-and-recovery.md).
- Read [the full-SDK capability/conflict matrix](../../../70-meta-wearables/15-full-sdk-capability-and-source-conflict-matrix.md), [application architecture](../../../70-meta-wearables/19-application-architecture-and-platform-boundaries.md), and [the Android API atlas](../../../70-meta-wearables/20-dat-android-api-surface-atlas.md) when platform identity, release build, or fallback is involved.
- Read the [version-dependency and device-compatibility route](../../../70-meta-wearables/26-version-dependency-and-device-compatibility-evidence.md) when project/version/channel work includes firmware, companion/DAT-app versions, support tables, or a Gen 2/Gen 3 compatibility claim.
- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md) when project identity, callbacks, Developer Mode, release attestation, package/signing credentials, or App Store/privacy-manifest review is involved.
- Refresh the official [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat), [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/), [onboarding and organization guide](https://wearables.developer.meta.com/docs/onboarding-and-organization-management), [manage projects](https://wearables.developer.meta.com/docs/manage-projects), [release channels](https://wearables.developer.meta.com/docs/set-up-release-channels), and [DAT iOS/Android repositories](https://github.com/facebook/meta-wearables-dat-ios), [Android repository](https://github.com/facebook/meta-wearables-dat-android).
- Read [the operations contract](references/developer-operations-contract.md) before producing an account, channel, tester, telemetry, or recovery packet.

## Authority and action boundary

1. The authenticated Developer Center/account state for the named organization,
   team, project, version, channel, and tester.
2. The current official Developer Center instructions and raw reference.
3. The selected DAT package/changelog and target build.
4. Historical examples, screenshots, or remembered account behavior.

Public documentation can describe a control; it cannot prove that the current
account can see or mutate it. Keep `source`, `access-gated`, `account`, `build`,
`connected`, `physical`, `signed`, and `release-channel` evidence separate.
Do not create, delete, restore, invite, remove, publish, or switch an external
account/project/channel unless the user explicitly authorizes that exact live
operation and the target is resolved.

## Fast path

Classify the requested action as read-only, reversible configuration, or release-affecting before touching Developer Center. For read-only work, gather identity/version/channel/tester state; for mutation, require explicit approval and a pre/post receipt, and stop on an account or access mismatch.

## Operations workflow

1. Freeze company, Managed Meta Account (MMA) organization, Wearables team,
   operator role, project, platform app, bundle/package ID, target build,
   product version, channel, tester Meta Account, and evidence level.
2. Check whether the company already has an MMA organization. Preserve the
   one-organization-per-company boundary; do not create a duplicate as a
   workaround for missing access.
3. Verify team membership and distinguish MMA organization membership from the
   separate Meta Account used by a tester to receive a release invitation.
4. Map project configuration: platform app identity, application ID/client
   token mode, product name/icon, permissions requested, internal permission
   justification, callback/build configuration, and privacy owner.
5. Map versioning and distribution: Major/Minor/Patch intent, generated DAT
   application build status, version details, one version per channel, invite
   mode, tester access, and the corresponding signed mobile build/URL.
6. Reconcile Developer Mode and release-channel state. Developer placeholders
   and local logic do not prove attestation, channel membership, or production
   readiness.
7. Audit telemetry and crash settings separately from product privacy: list
   collected operational categories, opt-out configuration, disclosure,
   retention, deletion, and reviewer-facing permission rationale.
8. For access, build, channel, or registration failure, record the exact first
   failure and bounded recovery. Do not retry blindly or turn a source
   instruction into an observed account result.

## Identity and distribution map

| Layer | Owns | Must not be confused with |
| --- | --- | --- |
| MMA organization | company-level membership and admin control | a tester Meta Account or DAT project |
| Wearables team | developers who can manage the Developer Center workspace | an iOS/Android app target |
| Project | product-level configuration and versions | a package/artifact or physical pair |
| Platform app | iOS bundle/package identity and app attestation configuration | a consumer product label such as Gen 2/Gen 3 |
| Version | immutable product/configuration snapshot for distribution | the SDK package version alone |
| Release channel | tester distribution and selected version | Developer Mode or public App Store/Play approval |
| Meta AI app state | connected-app permissions and selected channel on a tester device | account authorization or physical capability proof |
| DAT app on glasses/firmware | runtime provisioning and compatibility | project configuration or signed build evidence |

## Required output

- named organization/team/project/platform/operator and access state, with
  secrets and private account identifiers redacted;
- project/configuration matrix for iOS, Android, and Web Apps as applicable;
- product listing and permission-justification review;
- version/build/channel/tester matrix with Developer Mode versus signed
  release distinction;
- telemetry/crash opt-out and product privacy/retention/deletion separation;
- first failure, bounded recovery, and post-action state;
- exact evidence IDs from the operations contract;
- unresolved access, account, package, device, firmware, tester, channel, and
  production gates.

## Hard boundaries

- Never print, commit, paste into fixtures, or archive GitHub tokens, client
  tokens, application IDs paired with secrets, invitations, emails, device
  identifiers, or private diagnostics.
- Never treat a public guide, API reference, build status, invitation sent, or
  Developer Center screenshot as proof that a tester accepted, a device
  registered, or a physical capability worked.
- Never equate an MMA organization with a tester Meta Account; preserve both
  identity systems and their distinct access paths.
- Never equate Developer Mode with attested release-channel distribution,
  signed Android/iOS delivery, App Store/Play approval, or production.
- Never equate a callback, application ID, client token, app signature, channel,
  or attestation result with permission, physical capability, or on-device
  processing; keep the values and callback payloads redacted.
- Never treat telemetry opt-out or crash opt-out as a complete privacy program;
  audit collection, purpose, disclosure, retention, deletion, and permission
  justification separately.
- Never delete or restore a project, revoke a tester, switch a channel, or
  publish a version without explicit live-operation authorization and a named
  target.
- Never infer Gen 3 support, Display capability, or device compatibility from
  project configuration or product listing text.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Route planner](../meta-wearables-route-planner/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Android API atlas](../meta-dat-android-api-atlas/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)
- [Source refresh](../meta-wearables-source-refresh/SKILL.md)
- [Security and attestation](../meta-wearables-security-attestation/SKILL.md)

## Sources

- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Onboarding and organization management](https://wearables.developer.meta.com/docs/onboarding-and-organization-management)
- [Manage projects](https://wearables.developer.meta.com/docs/manage-projects)
- [Set up release channels](https://wearables.developer.meta.com/docs/set-up-release-channels)
- [Full security/attestation reference](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
