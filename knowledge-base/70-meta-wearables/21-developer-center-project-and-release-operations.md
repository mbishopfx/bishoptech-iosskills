# Developer Center, project, and release operations

This route owns the account and distribution layer around Meta Wearables DAT and
Ray-Ban Display Web Apps. It was refreshed on 2026-08-22 against the public
DAT-filtered reference (`v0.9`) and official Developer Center entry points. It
does not claim access to a specific account, project, tester, channel, build,
physical pair, or production release.

## What this route is—and is not

The Developer Center is the administrative path for organization/team access,
projects, platform app configuration, permissions, versions, release channels,
and tester distribution. It is not a third “regular SDK,” a replacement for the
selected DAT artifact, or proof that a connected device supports a capability.

```text
company/MMA check
  -> Wearables team membership
  -> project
  -> iOS/Android/Web platform identity and configuration
  -> product listing + permission justification
  -> integration version + generated DAT application build
  -> invite-only release channel + tester Meta Account
  -> Meta AI app channel/permission state
  -> selected DAT/Web App build + device/firmware operation
  -> telemetry/privacy/recovery receipt
```

Public raw documentation is `source` evidence. The interactive Developer Center,
account membership, build status, invitation acceptance, and channel state are
`access-gated`/`account` evidence until observed in the authorized project.

## Identity layers

| Layer | Purpose | Evidence and boundary |
| --- | --- | --- |
| Managed Meta Account (MMA) organization | One company-level organization and membership boundary | Check with the company before creating anything; do not create a duplicate organization. |
| Wearables team | Developer Center contributors for the project workspace | Team membership requires the same MMA organization; an invite is not acceptance proof. |
| Project | Product-level configuration and distribution container | A project is not an SDK package, mobile target, or physical device. |
| Platform app | iOS bundle/package identity and app attestation details | If iOS and Android identifiers differ, the public guide says to configure separate platform apps; verify the current account UI. |
| Product listing | App name/icon shown in Meta AI connected-app permission surfaces | Listing text does not establish permissions, device capability, or Gen 3 support. |
| Permission rationale | Internal justification for camera, microphone, and voice-invocation access | Rationale is not end-user consent, OS permission state, or privacy approval. |
| Integration version | Versioned project/configuration snapshot | SDK package version and Developer Center integration version are distinct. |
| Release channel | Distribution selection for invited tester Meta Accounts | Channel membership is not a signed App Store/Play release or physical capability result. |
| Meta AI app state | Connected-app permissions and selected channel on a tester device | Account authorization is not physical capability proof. |
| DAT app/firmware | Runtime provisioning and compatibility | Project configuration or signed build evidence does not prove this state. |

## Project configuration contract

Before a target build is prepared, record:

- project and platform app ownership, with credentials redacted;
- iOS bundle ID, Android package name, Web App URL, and callback/configuration
  path as applicable;
- application ID/client-token mode: Developer Mode placeholders versus release
  credentials supplied by the authorized project;
- product name, icon requirements, permissions requested, internal permission
  justification, and user-facing privacy/consent copy;
- selected DAT artifact/tag, target build, Web App revision/URL, and phone
  fallback;
- ownership for account, privacy, target build, device proof, and release.

Never put client tokens, GitHub package tokens, invitation email addresses, or
private project identifiers into this knowledge base or a portable skill archive.

## Versions and build readiness

The public reference describes Major, Minor, and Patch integration versions:

| Version intent | Use | Required record |
| --- | --- | --- |
| Major | breaking behavior/API or compatibility change | migration, selected package, target build, and fallback |
| Minor | backward-compatible feature addition | capability gate, permission/privacy impact, and test plan |
| Patch | bug fix or small non-breaking correction | affected operation, regression evidence, and rollback path |

DAT v0.7+ documentation describes a generated Device Access Toolkit app for a
new project version. Distribution must wait for its build status: `N/A`, `In
Progress`, `Ready`, or `Failed`. `Ready` establishes an account/build gate only;
it does not prove registration or physical glasses behavior.

## Release channels and testers

The public route currently describes invite-only channels. Each channel selects
one version at a time; the same version can be attached to multiple channels.
Testers use Meta Accounts, distinct from MMA organization membership. Record:

- channel name/description and selected integration version;
- tester status: invited, accepted, declined, removed, or unknown;
- tester’s Meta AI app channel selection and connected-app permission state;
- target app build/URL, DAT artifact, phone OS, Meta AI version, firmware, and
  exact operation;
- whether removing a tester changes future access only or also affects an
  already-registered app (the public guide says removal does not unregister the
  connected app automatically).

Do not treat an invitation email, channel creation, or channel switch as device
registration, Display installation, audio/camera success, release approval, or
production evidence.

## Developer Mode versus release distribution

| Mode | What it can establish | What it cannot establish |
| --- | --- | --- |
| Developer Mode | local app setup, source/compile/mock work, and authorized development flow | attested identity, tester channel access, signed distribution, production, or physical capability by itself |
| Invite-only release channel | signed/versioned distribution to accepted Meta Accounts | App Store/Play approval, physical operation, or broad public availability |
| Production/public | only the exact approved/published path if observed | no generalization to another device, firmware, or generation |

Keep application ID/client-token configuration, mobile build identity,
release-channel version, and physical runtime tuple in separate fields.

## Telemetry and privacy boundary

The public reference describes operational/diagnostic telemetry such as device
identifiers, firmware versions, session durations, error types, success/failure
flags, registration/permission/attestation flow, and performance markers. It
also describes default-enabled collection and platform opt-out metadata:

- Android: `com.meta.wearable.mwdat.ANALYTICS_OPT_OUT=true` in the manifest;
- iOS: `MWDAT > Analytics > OptOut = true` in `Info.plist`.

The Android README and 0.9.0 changelog also document
`com.meta.wearable.mwdat.CRASH_REPORTING_OPT_OUT=true`; iOS documents the
corresponding `MWDAT > CrashReporting > OptOut = true` control. Both defaults
are enabled unless the app opts out. These controls change DAT collection or
SDK crash capture only; they do not decide product consent, retention,
deletion, vendor processing, or App Store/Play/Meta policy compliance.

Treat these as source/API configuration signals, then verify the selected SDK
version and target build. Telemetry opt-out and crash-reporting opt-out do not
replace product disclosure, consent, minimization, retention, deletion, vendor
processing, or App Store/Play/Meta policy review.

## Recovery and destructive operations

Record first failure, action, and post-state for project build failures, channel
access, invitation problems, registration, and permissions. Do not create an
unbounded retry loop or hide the first error.

The public guide describes project removal prerequisites, a recovery period, and
restoration behavior. Treat removal, restore, member removal, tester revocation,
channel switching, and publication as destructive/state-changing operations:
resolve the exact target and obtain explicit authorization before acting. A
documentation route is not permission to mutate the user’s account.

## Evidence packet

| ID | Task | Minimum evidence | Not proven |
| --- | --- | --- | --- |
| `DCO-SOURCE-01` | Reopen source and record revision/date/access state. | `source` | account access |
| `DCO-ORG-01` | Resolve MMA organization, Wearables team, and operator role. | `account` | project/tester state |
| `DCO-PROJECT-01` | Inspect platform app/config/listing/permission rationale. | `account`/`static` | target compile or device behavior |
| `DCO-VERSION-01` | Record version intent and DAT build status. | `account`/`release` | tester acceptance or physical operation |
| `DCO-CHANNEL-01` | Record channel, version, invite mode, and tester list. | `account`/`release-channel` | registration or production |
| `DCO-TESTER-01` | Observe tester acceptance, Meta AI channel, and connected-app permissions. | `account`/`connected` | camera/audio/Display success |
| `DCO-TELEMETRY-01` | Verify telemetry categories, opt-out, privacy, retention, and deletion. | `static`/`release` | blanket compliance |
| `DCO-RECOVERY-01` | Execute one bounded account/build/channel recovery and record post-state. | `account`/`release-channel` | unobserved recovery or retry success |

## Sources

- [DAT-filtered full reference](https://wearables.developer.meta.com/llms.txt?full=true&product=dat)
- [Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/)
- [Onboarding and organization management](https://wearables.developer.meta.com/docs/onboarding-and-organization-management)
- [Manage projects](https://wearables.developer.meta.com/docs/manage-projects)
- [Set up release channels](https://wearables.developer.meta.com/docs/set-up-release-channels)
- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
