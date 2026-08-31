# Security and attestation contract

Use this reference as the compact handoff schema for the security specialist.
It records the intended boundary without storing the values being protected.

## Identity record

```yaml
surface: dat-ios | dat-android | native-display | web-app
target: named app target or hosted origin
package_revision: exact SPM tag/commit or Maven coordinates/revision
project_state: source | access-gated | observed
platform_identity:
  bundle_id_or_application_id: redacted
  package_name: redacted
  callback_scheme: redacted
  callback_host: absent | redacted | observed
  meta_app_id: absent | placeholder | redacted | observed
  client_token: absent | placeholder | redacted | observed
  team_id: absent | redacted | observed
  app_signature: absent | redacted | observed
mode: developer | release-channel | production | unknown
channel: absent | named-redacted | observed
attestation: not-applicable | not-used-in-developer-mode | not-run | passed | failed | unknown
```

`redacted` means the value exists and was checked without exposing it. It does
not mean that the account, identifier, token, signature, or channel is valid.

## Configuration matrix

| Check | iOS | Android | Web App | Result vocabulary |
| --- | --- | --- | --- | --- |
| Target identity | Bundle ID and registered app ID | package/application ID and signed variant | exact HTTPS origin/revision | `source`, `static`, `build`, `to-verify` |
| Registration callback | `AppLinkURLScheme` and `handleUrl` path | intent-filter scheme and activity callback | add/launch path through Meta AI | `present`, `validated`, `rejected`, `not-run` |
| Project identity | `MetaAppID`, `ClientToken`, `TeamID` as selected | `APPLICATION_ID`, `CLIENT_TOKEN` | no native DAT tuple established | `placeholder`, `redacted`, `observed`, `unknown` |
| Package access | SPM package resolution | GitHub Packages token in environment/local secure config | host/deployment credentials server-side | `redacted`, `not-exposed`, `failed`, `not-run` |
| Privacy/review | Info.plist, entitlements, privacy manifest, App Store gate | Manifest/runtime permissions, signing, Play policy | origin, client-visible data, host policy | `static`, `account`, `release`, `to-verify` |

## Callback outcome contract

For each callback attempt, retain only:

- run ID and platform/build variant;
- expected environment label and owned scheme/host label;
- `accepted`, `rejected`, `malformed`, `unexpected-environment`, `stale`, or
  `duplicate` outcome;
- SDK handler result category and the next registration/session state;
- redaction check and deletion/retention decision.

Do not retain the raw URL, query, fragment, account identifier, client token, or
device identifier. A callback outcome is not registration or permission proof
until the corresponding state is observed.

## Security evidence rows

| ID | Minimum evidence | Does not prove |
| --- | --- | --- |
| `SEC-SOURCE-01` | Official reference/repository URLs, revision/date, selected package/artifact, and source conflicts recorded | target configuration or current account behavior |
| `SEC-STATIC-01` | Bundle/package/callback/identity keys, variant, privacy metadata, and signing inputs inspected with values redacted | compile, attestation, channel, or device behavior |
| `SEC-CREDENTIAL-01` | Package/client/signing secrets remain in approved environment/config and scans/logs/artifacts are clean | credential validity or account authorization |
| `SEC-CALLBACK-01` | Owned callback scheme/host, malformed/stale/duplicate handling, SDK handoff, and no raw payload logging verified | registration, permission, session, or physical capability |
| `SEC-ATTEST-01` | Release-mode project identity and attestation result observed for the exact build | local processing, physical hardware, or public approval |
| `SEC-DEVMODE-01` | Developer Mode and placeholder behavior observed on the named target | attested release, signed distribution, or production |
| `SEC-CHANNEL-01` | Exact signed build, channel/version, tester account state, and Meta AI connection observed | camera/audio/Display/sensor behavior or App Store/Play approval |
| `SEC-PHYSICAL-01` | Security-sensitive operation repeated on the named device/firmware/companion/build tuple with redacted evidence | another model, generation, or processing path |
| `SEC-RELEASE-01` | Current App Store/Play/Meta release eligibility and exact distribution result checked | future policy, broad availability, or production beyond the observed path |

## Source-conflict notes

- The raw full reference lists iOS `AppLinkURLScheme`, `MetaAppID`, `ClientToken`,
  and `TeamID` for configuration/attestation; the current iOS upstream
  getting-started role shows a Developer Mode `MetaAppID` placeholder. Treat
  placeholder values as mode-specific guidance and resolve the selected
  package/build before release.
- Android upstream guidance uses `mwdat_application_id` and
  `mwdat_client_token` placeholders of `0` in Developer Mode and describes
  `APPLICATION_ID`/`CLIENT_TOKEN` as release credentials. Do not reuse an
  Android manifest recipe for iOS.
- Meta's raw reference currently warns that DAT App Store submission is not
  supported at this snapshot because of the current `ExternalAccessory`/MFi/
  privacy-manifest route. Re-open the current Meta and Apple review sources
  before making a release decision.
- Attestation and “on-device” are independent claims. The source describes
  app authenticity; processing location requires the implementation/data-flow
  and its own evidence.
