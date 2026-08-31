---
name: meta-wearables-security-attestation
description: Audit Meta Wearables DAT iOS and Android identity, attestation, callback, release-channel, package-token, privacy-manifest, and secret-handling boundaries. Use when configuring Developer Mode or release builds, reviewing MetaAppID/ClientToken/application IDs, diagnosing registration failures, protecting Android package credentials, validating callback inputs, or making on-device and publishing claims for native DAT or Ray-Ban Display Web Apps.
---

# Meta Wearables security and attestation

Own the security boundary between an iOS/Android app, Meta AI callbacks, the
Wearables Developer Center, DAT attestation, release channels, package
credentials, and the actual processing/data path. Return a redacted,
source-grounded configuration and evidence packet; this role is not a security
certification and does not grant access to a project or account.

## Read before acting

- Read the [security, attestation, and credential-boundaries route](../../../70-meta-wearables/25-security-attestation-and-credential-boundaries.md), its [contract reference](references/security-attestation-contract.md), and the [evidence packet](../../../70-meta-wearables/12-device-and-release-evidence-packet.md).
- Read [registration and configuration](../../../70-meta-wearables/02-registration-permissions-and-configuration.md), [Developer Center operations](../../../70-meta-wearables/21-developer-center-project-and-release-operations.md), [privacy/publishing](../../../70-meta-wearables/08-privacy-publishing-and-release.md), and [on-device compliance](../../../70-meta-wearables/17-on-device-compliance-and-runtime-contract.md).
- Read the selected [DAT iOS integration](../meta-dat-ios-integration/SKILL.md), [DAT Android integration](../meta-dat-android-integration/SKILL.md), [application architecture](../meta-wearables-app-architecture/SKILL.md), and [operational readiness](../meta-wearables-operational-readiness/SKILL.md) roles when the identity or callback is part of a build or recovery.
- Refresh the official [full reference](https://wearables.developer.meta.com/llms.txt?full=true), [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md), [DAT iOS permissions/registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md), [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md), [DAT Android permissions/registration](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/permissions-registration/SKILL.md), [manage projects](https://wearables.developer.meta.com/docs/develop/dat/manage-projects/), and [release channels](https://wearables.developer.meta.com/docs/set-up-release-channels/).
- Recheck Apple's [ExternalAccessory](https://developer.apple.com/documentation/externalaccessory), [privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files), [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), and the target's actual `Info.plist`, entitlements, privacy manifest, signing, and build settings.

## Fast path

Normalize the identity tuple before making security claims. Classify each value as secret or non-secret and each callback or attestation as source, configuration, runtime, or release evidence; audit one trust transition end-to-end and stop at its first missing authority.

## Workflow

1. **Freeze the identity tuple.** Record platform, bundle ID or Android
   application ID/package, URL callback scheme, selected DAT package/artifact,
   project/platform app, build variant, phone OS, Meta AI version, firmware,
   mode, channel, and target device. Keep unknowns `to-verify`.
2. **Classify the surface.** Native DAT uses mobile app identity and the Meta AI
   registration callback. Native Display is a DAT capability, not a separate
   credential system. A Web App uses a hosted HTTPS origin and its own
   distribution/host controls; do not invent a native attestation tuple for it.
3. **Inspect configuration without exposing values.** Verify key names,
   placement, bundle/package alignment, URL handling, permissions, privacy
   metadata, package repository access, and release/debug variant separation.
   Report presence, source, and redacted fingerprints—not credential values.
4. **Separate Developer Mode from release attestation.** Developer Mode is a
   local testing path whose registration/attestation behavior differs from a
   release-channel build. A Developer Mode success is not release identity,
   tester access, signing, physical capability, or production proof.
5. **Audit callback and package boundaries.** Let the selected SDK handle the
   documented callback, accept only the app-owned scheme/host expected by the
   target, do not log raw callback URLs or query values, and reject malformed,
   replayed, unexpected, or cross-environment input before changing state.
   Keep GitHub package tokens in the authorized environment only.
6. **Audit the data path separately.** Attestation authenticates an app/project
   relationship as described by the source; it does not establish that media,
   sensors, transcripts, or Display content stay on-device. Route processing,
   network, storage, consent, retention, and deletion to the on-device/privacy
   roles.
7. **Collect bounded evidence.** Use `SEC-*` rows for source, static config,
   redaction, callbacks, mode, attestation, channel, physical operation, and
   release. Keep account, signed, connected, physical, and App Store/Play
   outcomes separate.

## Identity map

| Surface | Identity/configuration to inspect | Security/evidence boundary |
| --- | --- | --- |
| DAT iOS | Registered bundle ID; `AppLinkURLScheme`; `MetaAppID`; `ClientToken`; `TeamID`; Meta AI query-scheme allowlist; selected SPM package and build variant | The public reference describes the keys for iOS attestation and callback setup. Upstream development guidance uses a Developer Mode placeholder for `MetaAppID`; resolve the exact selected package/build rather than copying a production value into examples. |
| DAT Android | Android package/application ID; `mwdat_application_id`; `mwdat_client_token`; callback intent-filter scheme; GitHub Packages repository access; signing/build variant | The public reference describes `APPLICATION_ID` and `CLIENT_TOKEN` for attestation and says Developer Mode can use `0` placeholders. A package token for Maven access is a separate secret and must never enter source, logs, fixtures, or archives. |
| Native Display | The selected DAT identity plus the runtime Display capability and session | Display rendering/input does not create a new trust boundary or prove the app is attested, the device is supported, or the content is private. |
| Ray-Ban Display Web App | Exact HTTPS origin/URL, deployed revision, host access controls, client-visible assets, distribution/add-to-device state | The reviewed public Web App route is hosted web content, not a native DAT package. Public URL, browser simulator, Meta AI connection, and physical Display launch are separate evidence. |

## Developer Mode, attestation, and release

Use this table as a claim firewall:

| State | Can establish | Cannot establish |
| --- | --- | --- |
| Source/configuration | The documented keys, flow, and intended variant are understood | Current account access, correct secret values, compile success, attestation success, or device behavior |
| Developer Mode | A local development registration path when the companion/device prerequisites are observed | Release-channel identity, attestation, signed distribution, public availability, or production |
| Attested release-channel build | The authorized project identity, selected version/channel, and app attestation path for the exact build when observed | Camera/audio/Display/sensor behavior, on-device processing, App Store/Play approval, or broad generation support |
| Physical run | The named operation on the exact model/firmware/companion/build tuple | Another model, “Gen 3,” another channel, or a different processing/network path |
| Web App deployment | The exact hosted URL and deployed web revision | Native DAT attestation, private origin, offline/sensor support, or physical MRBD behavior without its own run |

The current raw Meta reference says DAT App Store submission is not currently
supported at this snapshot and attributes the issue to the present
`ExternalAccessory`/MFi/privacy-manifest path. Treat that as a dated Meta
release gate to recheck with the exact package and Apple review requirements,
not as a permanent policy or as a Play-store conclusion.

## Callback and credential controls

- Keep the callback scheme unique to the target app/environment. Parse the URL
  using the platform API and pass it to the documented DAT handler; do not build
  app state from arbitrary query, fragment, or host values.
- Reject a callback when its scheme/host/environment does not match, it cannot
  be parsed, it arrives after the registration/session epoch has ended, or it
  would cross a debug/release boundary. Record only a stable local outcome such
  as `callback_rejected`.
- Store `ClientToken`, `GITHUB_TOKEN`, package credentials, signing material,
  private project identifiers, and invitation data in the authorized build/CI
  mechanism. Use placeholder names in examples and redacted presence checks in
  evidence.
- Do not print credentials with build tools, shell tracing, Gradle diagnostics,
  Xcode logs, crash reports, screenshots, model context, or portable archives.
  Check generated artifacts and archive paths before sharing them.
- Treat application IDs, bundle/package identifiers, callback URLs, device
  identifiers, tester/account identifiers, and signatures as sensitive project
  metadata even when an individual value may be public. Minimize, redact, and
  avoid joining values unnecessarily in logs.
- An “on-device” label requires a separate processing-location declaration. A
  trusted callback or attested app can still send camera/audio/sensor data to a
  phone or network service.

## Required handoff

Return:

- exact platform, target, package/artifact revision, project/platform-app
  identity status, build variant, callback route, and mode/channel;
- a redacted key-presence/configuration matrix with source and target/static
  status;
- callback validation, environment separation, token/secret storage, logging,
  artifact, and retention controls;
- attestation, Developer Mode, tester/channel, signing, physical, and
  App Store/Play evidence rows with `not-run`, `access-gated`, or `to-verify`
  where appropriate;
- the processing-location/network/storage boundary and handoff to privacy and
  on-device compliance;
- first failure and one bounded recovery when diagnosing registration or
  release behavior;
- explicit non-claims, especially no invented Gen 3 mapping and no claim that
  attestation proves physical capability or local processing.

## Hard boundaries

- Never print, commit, archive, or paste a real token, client credential,
  signing value, invitation address, private project identifier, callback
  payload, device serial, or raw diagnostic bundle.
- Never equate `MetaAppID`, `ClientToken`, Android application ID, a bundle ID,
  a package token, or an app signature with one another; record their roles and
  target platform separately.
- Never call Developer Mode an attested release, or a release channel an App
  Store/Play approval or production result.
- Never infer that a valid callback proves registration, permissions, session,
  camera, audio, Display, sensor, or on-device processing success.
- Never claim a public Web App has native DAT attestation or secret storage in
  the browser. Keep private credentials server-side and review the public
  origin/data path.
- Never infer “Gen 3” from a consumer label, product announcement, enum name,
  or neighboring model. Require runtime identity, firmware, capability, and a
  named physical result.
- Stop before mutating a Developer Center project, channel, tester list, or
  release state unless the user explicitly authorizes the exact live operation
  and target.

## Related routes

- [Meta agentic team](../meta-wearables-agentic-team/SKILL.md)
- [Developer Center operations](../meta-wearables-developer-operations/SKILL.md)
- [DAT iOS integration](../meta-dat-ios-integration/SKILL.md)
- [DAT Android integration](../meta-dat-android-integration/SKILL.md)
- [Privacy and publishing](../meta-wearables-privacy-publishing/SKILL.md)
- [On-device compliance](../meta-wearables-on-device-compliance/SKILL.md)
- [Operational readiness](../meta-wearables-operational-readiness/SKILL.md)
- [Application architecture](../meta-wearables-app-architecture/SKILL.md)
- [Device proof](../meta-wearables-device-proof/SKILL.md)

## Sources

- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS permissions and registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md)
- [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md)
- [DAT Android permissions and registration](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/permissions-registration/SKILL.md)
- [Wearables Developer Center manage projects](https://wearables.developer.meta.com/docs/develop/dat/manage-projects/)
- [Wearables release channels](https://wearables.developer.meta.com/docs/set-up-release-channels/)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
