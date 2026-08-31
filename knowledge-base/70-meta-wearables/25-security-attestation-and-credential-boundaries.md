# Security, attestation, and credential boundaries

This route owns the security and identity boundary between a Meta Wearables
mobile app, Meta AI callbacks, the Wearables Developer Center, DAT attestation,
release channels, package credentials, and the actual processing/data path. It
was refreshed on 2026-08-22 against the public v0.9 full reference and the
current upstream DAT iOS/Android setup and permissions roles. It is an
implementation and evidence contract, not a security certification or proof of
access to a particular account, project, build, or device.

## Why this is a separate route

Registration failures and unsafe claims often look like one problem but cross
several trust boundaries:

```text
mobile target identity
  -> Meta AI callback and registration
  -> Developer Center project/platform app
  -> Developer Mode or release-channel identity/attestation
  -> signed build and companion/device state
  -> transport/session/capability
  -> camera/audio/sensor/Display processing and data flow
```

A valid callback does not prove permissions, a session, a physical capability,
or local processing. An attested app does not automatically keep media on the
phone or glasses. A Web App URL is a different distribution and security
surface from a native DAT package.

## Identity tuple

Freeze these fields before diagnosing registration, building a release, or
making a security/on-device claim:

| Surface | Identity/configuration to inspect | Evidence boundary |
| --- | --- | --- |
| DAT iOS | Registered bundle ID; `AppLinkURLScheme`; `MetaAppID`; `ClientToken`; `TeamID`; Meta AI query-scheme allowlist; selected SPM package and build variant | The full reference describes these iOS keys for callback/configuration and attestation. The current iOS upstream getting-started role uses a Developer Mode placeholder for `MetaAppID`; resolve the exact selected package/build rather than copying a production value into examples. |
| DAT Android | Android package/application ID; `mwdat_application_id`; `mwdat_client_token`; callback intent-filter scheme; GitHub Packages repository access; signing/build variant | The full reference describes `APPLICATION_ID` and `CLIENT_TOKEN` for attestation and says Developer Mode can use `0` placeholders. A GitHub package token is a separate secret and must never enter source, logs, fixtures, or archives. |
| Native Display | The selected DAT identity plus runtime Display capability and session | Native Display rendering/input does not create a separate credential system or prove attestation, support, privacy, or physical behavior. |
| Ray-Ban Display Web App | Exact HTTPS origin/URL, deployed revision, host controls, client-visible assets, and Meta AI add/launch state | The reviewed Web App route is hosted web content, not a native DAT package. Public URL, browser simulator, Meta AI connection, and physical Display launch remain separate evidence. |

Keep values redacted in packets. Record `absent`, `placeholder`, `present`,
`redacted`, or `observed` plus the source/build that was inspected; do not
paste the value merely because the field is needed for a checklist.

## Developer Mode versus release attestation

| State | What it can establish | What it cannot establish |
| --- | --- | --- |
| Source/configuration | The documented keys, flow, and intended variant are understood | Current account access, secret validity, compile success, attestation success, or device behavior |
| Developer Mode | A local development registration path when the companion/device prerequisites are observed | Release-channel identity, attestation, signed distribution, public availability, or production |
| Attested release-channel build | The authorized project identity, selected version/channel, and attestation path for the exact build when observed | Camera/audio/Display/sensor behavior, on-device processing, App Store/Play approval, or broad generation support |
| Physical run | The named operation on the exact model/firmware/companion/build tuple | Another model, “Gen 3,” another channel, or a different processing/network path |
| Web App deployment | The exact hosted URL and deployed revision | Native DAT attestation, private origin, offline/sensor support, or physical MRBD behavior without its own run |

The raw Meta reference says Developer Mode allows unpublished apps to register
and interact with glasses and enables invite-only release-channel testing. It
also says iOS configuration includes `AppLinkURLScheme`, `MetaAppID`,
`ClientToken`, and `TeamID` for the identity/attestation path, while Android
uses `APPLICATION_ID` and `CLIENT_TOKEN`. The same reference says attestation
is not used in Developer Mode and that incorrect release identifiers prevent a
connection. Treat these as source claims until the selected target and account
are observed.

The current raw reference also warns that DAT App Store submission is not
currently supported and attributes the snapshot's issue to the current
`ExternalAccessory`/MFi/privacy-manifest path. Recheck this dated Meta warning
against the exact package and Apple's current review requirements; do not infer
anything about Play eligibility from it.

## Callback boundary

The Meta AI companion app returns to the mobile target through the configured
callback. The app should:

1. register only the intended environment-owned scheme/host;
2. parse the URL with the platform API and pass it to the documented DAT
   handler;
3. reject malformed, unexpected-environment, stale, duplicate, or
   cross-debug/release callbacks before mutating registration/session state;
4. record a stable local outcome such as `callback_rejected`, not the raw URL,
   query, fragment, account, token, or device identifier; and
5. prove the resulting registration/permission state separately from callback
   receipt.

Treat URL-scheme uniqueness and callback validation as engineering controls,
not as a claim that the public Meta source supplies a complete threat model.
The source establishes the callback's role; the target implementation must
still define ownership, parsing, replay/stale handling, and redaction.

## Credential and artifact boundary

| Material | Correct boundary | Never do |
| --- | --- | --- |
| iOS `MetaAppID`, `ClientToken`, `TeamID` | Authorized project/build configuration; inspect presence and variant without printing values | Paste real values into fixtures, screenshots, public source, logs, or portable skills |
| Android `APPLICATION_ID`, `CLIENT_TOKEN` | Developer Center project/build variant; keep release values separated from Developer Mode placeholders | Treat Android manifest keys as iOS keys or expose release credentials in a debug artifact |
| `GITHUB_TOKEN`/GitHub Packages access | Environment or secure local/CI configuration with least privilege such as the documented package-read scope | Commit it, echo it, put it in Gradle output, or archive the local properties file |
| Signing and provisioning material | Xcode/Gradle signing system and authorized CI | Copy private keys, signatures, profiles, or unredacted signing diagnostics into the KB |
| Callback payloads and account/device metadata | Short-lived, redacted local outcome records | Log raw query/fragment, tester email, serial, device ID, or private project data |
| Web App host/deployment secrets | Server-side host/CI boundary; only public assets reach the client | Put API keys or private tokens in browser JavaScript, source maps, or public assets |

Application IDs and callback URLs may be visible in some contexts, but the
safe packet default is to minimize and redact them, especially when joining
them with account, channel, device, signature, or diagnostic data.

## Attestation is not an on-device claim

Use separate columns for:

| Claim | Required statement |
| --- | --- |
| App identity | Which project/platform app and exact build identity were configured/observed? |
| Registration | Did the Meta AI callback produce the documented registered state? |
| Permission | Did the user grant the exact DAT permission on the named target? |
| Capability | Did the runtime report the capability, and did the physical operation work? |
| Processing location | Do the actual camera/audio/sensor/Display bytes stay on glasses, phone, local network, or remote service? |
| Distribution | Was the exact signed build installed through the named release channel or hosted URL? |

Attestation can support an app-authenticity statement from the documented
platform flow. It does not answer the processing-location, retention, consent,
thermal, network, or physical-capability questions. Send those fields to the
[on-device compliance route](17-on-device-compliance-and-runtime-contract.md),
[privacy/publishing route](08-privacy-publishing-and-release.md), and
[transport/reliability route](22-transport-audio-and-runtime-reliability.md).

## Evidence ledger

Use the following rows with the project evidence vocabulary:

| ID | Minimum evidence | Does not prove |
| --- | --- | --- |
| `SEC-SOURCE-01` | Official reference/repository URLs, revision/date, selected package/artifact, and source conflicts recorded | Target configuration or current account behavior |
| `SEC-STATIC-01` | Bundle/package/callback/identity keys, build variant, privacy metadata, and signing inputs inspected with values redacted | Compile, attestation, channel, or device behavior |
| `SEC-CREDENTIAL-01` | Package/client/signing secrets remain in the approved environment/config and scans/logs/artifacts are clean | Credential validity or account authorization |
| `SEC-CALLBACK-01` | Owned callback scheme/host, malformed/stale/duplicate handling, SDK handoff, and no raw-payload logging verified | Registration, permission, session, or physical capability |
| `SEC-ATTEST-01` | Release-mode project identity and attestation result observed for the exact build | Local processing, physical hardware, or public approval |
| `SEC-DEVMODE-01` | Developer Mode and placeholder behavior observed on the named target | Attested release, signed distribution, or production |
| `SEC-CHANNEL-01` | Exact signed build, channel/version, tester account state, and Meta AI connection observed | Camera/audio/Display/sensor behavior or App Store/Play approval |
| `SEC-PHYSICAL-01` | Security-sensitive operation repeated on the named device/firmware/companion/build tuple with redacted evidence | Another model, generation, or processing path |
| `SEC-RELEASE-01` | Current App Store/Play/Meta release eligibility and exact distribution result checked | Future policy, broad availability, or production beyond the observed path |

The current environment has source-level evidence only for this route. The
account, target build, attestation, channel, signed artifact, physical, App
Store/Play, and production rows remain `access-gated`, `not-run`, or
`to-verify` until a named operation closes them.

## Source conflicts and open gates

- The full reference lists the iOS identity keys, while the iOS upstream
  getting-started role shows a Developer Mode `MetaAppID` placeholder. Treat
  placeholder values as mode-specific guidance and resolve the selected
  package/build before release.
- Android's current upstream setup shows `0` placeholders for both manifest
  values in Developer Mode and release credentials from the Developer Center.
  Do not reuse that recipe for iOS or assume an exact Maven version from the
  moving skill text.
- The Developer Center's authenticated project, app, build, tester, channel,
  and compatibility state is account evidence, not a public-source fact.
- The raw v0.9 App Store warning is dated and should be re-opened before any
  publishing decision. Apple privacy-manifest/MFi requirements are platform
  review gates, not proof that a local prototype is shippable.
- No current public source maps the user's “Gen 3” wording to a DAT runtime
  `DeviceType`. Keep that label `to-verify` until the exact runtime, firmware,
  capability response, and named physical result are recorded.

## Sources

- [Full Meta Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md)
- [DAT iOS permissions and registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md)
- [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md)
- [DAT Android permissions and registration](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/permissions-registration/SKILL.md)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Manage projects](https://wearables.developer.meta.com/docs/develop/dat/manage-projects/)
- [Release channels](https://wearables.developer.meta.com/docs/set-up-release-channels/)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [Meta Wearables Web Apps](https://wearables.developer.meta.com/docs/develop/webapps)
- [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory)
- [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
