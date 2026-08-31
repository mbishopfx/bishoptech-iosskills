# Meta Wearables official source registry

This registry owns the primary links for the Meta Wearables lane. Last reviewed
2026-08-30. Current GitHub repositories under the `facebook` organization are
treated as official implementation/reference sources; legacy
`facebookincubator` links are retained only as historical provenance. The
Wearables Developer Center and Meta announcements remain authoritative for
current platform, account, preview, policy, and product claims.

## Revision anchors reviewed 2026-08-30

| Lane | Public revision observed | How to use it |
| --- | --- | --- |
| DAT iOS | `main` `225f64ff1617e7acc8c407bb8d3ee132f7263d00`; `0.9.0` tag `9b1b83d791dfebff7afd452e924a256819094b64` | Pin the tag for a reproducible package; treat `main` as a separately labeled refresh snapshot. |
| DAT Android | `main` `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc` | Use for current parity/source refresh only until the exact Gradle artifact/tag is recorded. |
| Web Apps | `main` `a2714f862c61b1ce9c6cb624fc7e4938087102db` | Use the toolkit for implementation guidance, but reconcile it with the full Developer Center index before calling a feature runtime-supported. |
| Source-pinned surface manifest | Local `meta-wearables-public-surface-2026-08-22`, schema version 1, `manifest_revision: 6`, bundled in the full-SDK audit package | Load for agent routing, terminology resolution, coverage accounting, the machine-checked upstream AI surfaces, and the official agent-surface install/MCP contract; it does not replace the selected package/API reference, authenticated account state, or physical/release proof. |
| Agent team manifest | Local `meta-wearables-agent-team-2026-08-22`, `manifest_revision: 4`, bundled with the agentic team package | Load for the exact 23-role local roster, 32 upstream role handoffs, source AI surfaces, official agent-surface contract, shared handoff contract, and Ray-Ban Display/Gen 2/Gen 3 gates; validate before delegating. |
| Source-tree inventory | Live checker `check_source_tree_inventory.py`, run 2026-08-30 with `CHECKS 23 DRIFT 0` | Re-run after the public-ref checker to verify the three root AI files, per-lane `.codex-plugin/plugin.json`, Package.swift products, plugin versions/exact role names and counts, sample roots/toolchains, Android artifacts, and Web Apps reference/example/template anchors. |
| Version-pinned API surface register | Local `meta-wearables-api-surface-2026-08-22`, 30 normalized rows in the full-SDK audit manifest | Load the journey-specific `IOS-*`, `AND-*`, `WEB-*`, and conceptual-index rows for source anchors, status, compile/runtime gates, privacy paths, fallbacks, and migrations; exact package/API and target evidence still win. |

The official repository READMEs are the current authority for agent/tooling
entry points: native DAT exposes a local Codex plugin install from the checked
out repository, Web Apps exposes the Meta Wearables marketplace route, and all
three official READMEs point to the shared public Wearables MCP. The native DAT
lookup is `search_dat_docs`; the Web Apps lookup is `search_webapps_docs`; the
README contract says the MCP requires no auth, OAuth, tokens, or custom
authorization headers. This workspace currently cannot call that MCP, so the
local team keeps a pinned repository/full-reference fallback and labels lookup
results as source evidence only.

## 2026-08-30 Web Apps repository relocation receipt

The public Web Apps toolkit moved from `facebookincubator/meta-wearables-webapp`
to `facebook/meta-wearables-webapp`. A live `git ls-remote` check recorded
`main` at `a2714f862c61b1ce9c6cb624fc7e4938087102db`. The GitHub compare from the
prior `24d7bfc553d33d7fe849cd70d04544b1de555896` snapshot reports one commit and
three changed files: `README.md`, `install-skills.sh`, and
`.cursor-plugin/plugin.json`. The diff updates repository/install metadata and
the simulator name; it does not change the API/runtime rows in the local
surface manifest.

The current manifest is therefore revision 6 and the team manifest is revision
4. This is source and routing evidence only. It does not prove a target build,
authenticated project, connected device, physical Display behavior, signing,
or release eligibility.

## Product naming and launch sources reviewed 2026-08-22

| Source | What it establishes | What it does not establish |
| --- | --- | --- |
| [Ray-Ban Meta (Gen 2) announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/) | Meta’s consumer product naming and launch-level feature context for Ray-Ban Meta Gen 2. | DAT artifact support, a runtime `DeviceType`, firmware compatibility, Display capability, or physical third-party-app behavior. |
| [Ray-Ban Meta Optics announcement](https://about.fb.com/news/2026/03/meta-ai-glasses-built-for-prescriptions/) | Meta’s separate Gen 2 Optics product naming and prescription-oriented product context. | A one-to-one mapping from the product name to a DAT package/artifact, camera/audio/Display capability, or named-device result. |
| [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/) | Meta’s official name for a separate 2026 Meta Glasses product line. | The label “Gen 3,” a public DAT runtime mapping, an authenticated compatibility table, or physical support for any selected capability. |

Product announcements own consumer naming and launch context. The selected
DAT package/artifact, generated API, authenticated Developer Center state, and
named physical target still own implementation and support claims. Do not turn
the user’s “Gen 3” shorthand into the official “Meta Glasses” label without a
separate runtime mapping receipt.

## Public plugin and skill surfaces reviewed 2026-08-22

| Surface | Public revision/version observed | How to use it |
| --- | --- | --- |
| DAT iOS Codex plugin | Repository `main` at `225f64ff...`; plugin manifest `0.9.0`; ten role skills under `plugins/mwdat-ios/skills` | Use the upstream role names for routing, but pair them with the selected DAT package and local evidence contract. |
| DAT Android Codex plugin | Repository `main` at `81dfb51b...`; plugin manifest `0.9.0`; ten conceptual role skills under `plugins/mwdat-android/skills` | Use for Android/Kotlin/Gradle/Manifest routing; do not infer Swift symbols or package parity from role-name similarity. |
| Web Apps toolkit plugin | Repository `main` at `a2714f8...`; plugin manifest `127.0.0`; twelve toolkit skills under `plugins/meta-wearables-webapp/skills` | Use the toolkit for Web App scaffolding and QA, while preserving the official full-reference conflict as `source-conflict`/`to-verify`. |

The Web Apps toolkit and the full Developer Center index currently conflict
about text composition, offline support, back navigation, extended gestures,
and sensors. The route pages and device packet preserve that conflict as
`source-conflict`/`to-verify`; it must not be silently resolved by whichever
source is easier to read.

The direct raw full-reference refresh currently identifies `DAT SDK v0.9` for
native mobile iOS/Android. The separate Web Apps toolkit and Developer Center
route covers hosted HTML/CSS/JavaScript on Meta Ray-Ban Display. This is the
terminology used here when a request says “regular SDK”; no third public native
SDK family was found in the reviewed official repositories.

## Native DAT

| Source | Use |
| --- | --- |
| [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios) | SPM identity, public AI guidance, samples, releases, and current iOS modules. |
| [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) | API renames/removals, minimum deployment, model enum, lifecycle, Display, MockDevice, and diagnostics drift. |
| [DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest) | Exact Swift symbol/signature reference; re-open in an authenticated context when required. |
| [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md) | Package setup, Info.plist, launch configuration, callback, registration, and first session. |
| [DAT iOS permissions/registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md) | Registration and device permission state. |
| [DAT iOS camera streaming](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/camera-streaming/SKILL.md) | Camera, stream, frames, photo capture, resolution, frame rate, and bandwidth. |
| [DAT iOS session lifecycle](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/session-lifecycle/SKILL.md) | Session/stream state, pause, availability, and stop behavior. |
| [DAT iOS Display Access](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md) | Display capability, DSL, device filter, link leases, playback, and teardown. |
| [DAT iOS MockDevice](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/mockdevice-testing/SKILL.md) | Deterministic device, permission, media, and captouch fixtures. |
| [DAT iOS sample apps](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples) | Current target configuration and end-to-end sample ownership. |
| [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android) | Cross-platform parity, Kotlin/Gradle/Manifest route, and Android changelog. |
| [DAT Android API reference](https://wearables.developer.meta.com/docs/reference/android/dat/latest) | Exact Kotlin/Java symbol and artifact reference; reopen for the selected resolved Maven version. |
| [DAT Android upstream skills](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android/skills) | Setup, permissions, camera, Display, lifecycle, MockDevice, debugging, and sample guidance; treat moving examples as source inputs, not artifact proof. |

## Developer Center and policy

| Source | Use |
| --- | --- |
| [Meta Wearables Developer Center](https://wearables.developer.meta.com/docs/develop/) | Current setup, account, compatibility, docs, and policy entry point. |
| [Onboarding and organization management](https://wearables.developer.meta.com/docs/onboarding-and-organization-management) | Managed Meta Account organization, team roles, membership, and the one-organization-per-company boundary. |
| [Manage projects](https://wearables.developer.meta.com/docs/develop/dat/manage-projects/) | Project/platform-app identity, product listing, permission rationale, versions, generated DAT app build state, and project recovery/removal behavior. |
| [Release channels](https://wearables.developer.meta.com/docs/set-up-release-channels) | Version distribution, invite-only tester Meta Accounts, channel switching, connected-app permissions, and release-channel evidence boundaries. |
| [DAT iOS API documentation root](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest) | Current symbol route. |
| [Mock Device Kit](https://wearables.developer.meta.com/docs/mock-device-kit) | Official mock behavior and sample usage. |
| [iOS Mock Device testing](https://wearables.developer.meta.com/docs/testing-mdk-ios) | iOS test-specific guidance. |
| [Meta Wearables MCP](https://mcp.developer.meta.com/wearables) | Live documentation search when the environment supports the public MCP. |
| [Developer Terms](https://wearables.developer.meta.com/docs/terms) | Developer preview and usage terms; recheck access requirements. |
| [Acceptable Use Policy](https://wearables.developer.meta.com/docs/acceptable-use-policy) | Policy boundary for integrations. |
| [DAT announcement](https://developers.meta.com/blog/introducing-meta-wearables-device-access-toolkit/) | Preview scope, camera/audio announcement, controlled tester distribution, and historical launch context. |
| [Full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true) | Public raw v0.9 index for native DAT, Web Apps, hardware families, audio, sensors, testing, release, and policy topic discovery; reconcile version-sensitive claims with the selected package and authenticated tables. |
| [Version dependencies](https://wearables.developer.meta.com/docs/version-dependencies) | Current companion/firmware/SDK compatibility table when accessible; exact values remain access-gated until observed in the selected account context. |
| [Known issues](https://wearables.developer.meta.com/docs/knownissues) | First-party operational issue entry point; classify public reports and target observations separately. |
| [Release-channel setup](https://wearables.developer.meta.com/docs/set-up-release-channels) | Project/application identity, tester, signed-channel, and distribution setup; not a substitute for a named release run. |

The interactive Developer Center development route rendered a login-gated
surface during the 2026-08-22 refresh. The raw
[`llms.txt?full=true`](https://wearables.developer.meta.com/llms.txt?full=true)
and DAT-filtered endpoint were readable as public v0.9 source text over HTTPS.
Treat authenticated compatibility tables, exact version-dependency values,
and policy details as `access-gated` until reopened through the logged-in
Developer Center or an authorized public MCP result; do not confuse that UI
access state with the readable raw reference index.

## Security, attestation, and credential boundaries

| Source | Use |
| --- | --- |
| [Full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true) | iOS `AppLinkURLScheme`/`MetaAppID`/`ClientToken`/`TeamID`, Android `APPLICATION_ID`/`CLIENT_TOKEN`, Developer Mode versus attestation, release-channel identity, and the dated DAT App Store warning. |
| [DAT iOS getting started](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/getting-started/SKILL.md) | iOS package setup, callback configuration, Developer Mode placeholder guidance, and target configuration. |
| [DAT iOS permissions/registration](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/permissions-registration/SKILL.md) | Meta AI registration, callback handling, permission state, and Developer Mode/release distinction. |
| [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md) | GitHub Packages access boundary, manifest placeholders, callback scheme, and Android attestation configuration. |
| [DAT Android permissions/registration](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/permissions-registration/SKILL.md) | Android Developer Mode versus production identity and registration prerequisites. |
| [Manage projects](https://wearables.developer.meta.com/docs/develop/dat/manage-projects/) | Project/platform-app identity, application credentials, version/build, and account-gated project state. |
| [Release channels](https://wearables.developer.meta.com/docs/set-up-release-channels/) | Invite-only distribution, tester Meta Accounts, version/channel state, and signed release evidence boundaries. |
| [Apple ExternalAccessory](https://developer.apple.com/documentation/externalaccessory) | Apple framework/review context for the current DAT App Store warning; recheck current requirements before publishing. |
| [Apple privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) | Privacy-manifest implementation and review gate; does not prove DAT eligibility. |
| [Apple App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Current App Store policy/review authority; do not turn the dated Meta warning into a permanent policy claim. |

The security route treats every credential and callback as redacted project
metadata. The public sources establish configuration roles and mode/channel
semantics; they do not establish the current account, target secret values,
attestation result, signing result, physical capability, processing location,
or App Store/Play/production eligibility.

## Version dependency and device compatibility

| Source | Use |
| --- | --- |
| [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) | Reproducible 0.9.0 camera/Display/listener migrations and release-sensitive iOS API facts. |
| [DAT Android changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md) | Reproducible 0.9.0 camera/Display/`DatResult`/DAM/R8 migrations and Android API facts. |
| [DAT Android package registry](https://github.com/facebook/meta-wearables-dat-android/packages) | Public artifact/version availability; not a target's resolved dependency graph or physical support. |
| [Wearables version dependencies](https://wearables.developer.meta.com/docs/develop/dat/version-dependencies/) | First-party companion/firmware/SDK compatibility authority when authenticated access is available; this refresh observed a login-gated page. |
| [Full public reference](https://wearables.developer.meta.com/llms.txt?full=true) | Hardware-family and version/dependency discovery; not an exact target support table. |
| [Public Gen 2 firmware report](https://github.com/facebook/meta-wearables-dat-ios/issues/265) | Community troubleshooting signal for a reported 0.9.0 Gen 2 firmware 126→127 failure; never classify it as official support policy. |

The compatibility role records the full phone/Meta AI/on-glasses DAT-app/
firmware/artifact/runtime tuple and uses `COMP-*` evidence rows. Product labels,
model enums, version numbers, registration, or a community issue do not establish
universal capability. “Gen 3” remains `to-verify` until a current official
mapping and named-device result exist.

## Transport and runtime reliability

| Source | Use |
| --- | --- |
| [DAT iOS 0.8/0.9 changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md) | Wi-Fi transport addition, camera lifecycle, background/sample behavior, and current iOS migration boundaries. |
| [DAT iOS README/setup](https://github.com/facebook/meta-wearables-dat-ios#readme) | Current iOS package/API reference link, local-network/Bonjour setup signal, HFP/A2DP and public MCP/tooling entry points. |
| [DAT Android README/setup](https://github.com/facebook/meta-wearables-dat-android#readme) | Current Android artifact setup, public Codex/plugin route, four 0.9.0 artifact coordinates, and shared docs MCP entry point. |
| [DAT Android 0.9 changelog](https://github.com/facebook/meta-wearables-dat-android/blob/main/CHANGELOG.md) | Android camera/Display/session lifecycle, Java/R8, DAM, thermal/power, and current migration surface; it does not by itself establish iOS-equivalent Wi-Fi parity. |
| [DAT Android getting started](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/getting-started/SKILL.md) | Android Bluetooth/Internet permissions, callback, `APPLICATION_ID`/`CLIENT_TOKEN`, and selected-artifact setup. |
| [Apple local-network privacy key](https://developer.apple.com/documentation/bundleresources/information_property_list/nslocalnetworkusagedescription) | iOS disclosure boundary for a target that actually uses local-network transport. |
| [Apple AVAudioSession](https://developer.apple.com/documentation/avfaudio/avaudiosession) | HFP/A2DP route, interruption, and audio-session ownership boundary. |
| [Android Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions) | Platform permission semantics; not proof that DAT negotiates a specific transport. |

The current source pass therefore treats iOS Wi-Fi as an explicit SDK signal,
Android Wi-Fi parity as `to-verify`, and all transport/processing claims as
separate from declared permissions and connected-device state.

## Debugging and observability

| Source | Use |
| --- | --- |
| [DAT iOS debugging skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/debugging/SKILL.md) | Read-only setup, Developer Mode, compatibility, registration, session, stream, logging, and first-party issue diagnosis. |
| [DAT iOS live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/live-debugging-mcp/SKILL.md) | Local DAT Inspector discovery, connection/readiness baseline, companion-boundary diagnosis, device path, narrow event waits, and redacted bundle export. |
| [DAT Android debugging skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/debugging/SKILL.md) | Android initialization, Developer Mode/build mode, registration, `DatResult`, session/stream, compatibility, and typed-failure diagnosis. |
| [DAT Android live-debugging MCP skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/live-debugging-mcp/SKILL.md) | Android counterpart to the read-only live-debugging loop and app-visible companion/device boundary evidence. |
| [Wearables MCP](https://mcp.developer.meta.com/wearables) | Documentation lookup; not a local debug connection, account mutation, target build, or physical-device proof. |

The current full-reference raw endpoint is reachable through direct HTTPS in
the shell refresh, while the interactive Developer Center/web retrieval can
render a login gate. Preserve that client/access distinction rather than
calling the reference universally public or universally unavailable.

## Web Apps

| Source | Use |
| --- | --- |
| [Web App AI toolkit](https://github.com/facebook/meta-wearables-webapp) | Official skills, templates, simulator, deployment, and supported Web App features. |
| [Web App README and AI toolkit](https://github.com/facebook/meta-wearables-webapp#readme) | Web Apps Codex marketplace/install-script route, `search_webapps_docs`, public HTTPS/browser/physical split, and 600×600 design constraints. |
| [Web App agent instructions](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md) | 600x600, MRBD metadata, D-pad/EMG, focus, performance, and on-device testing rules. |
| [Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md) | Additive display physics, color/contrast, input, and layout guidance. |
| [Performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md) | Viewport, asset, refresh, offline, and focus budgets. |
| [Meta Wearables Web Apps docs](https://wearables.developer.meta.com/docs/develop/webapps) | Current Developer Center route; re-open for exact Web App API and policy claims. |
| [Display Web App Simulator](https://chromewebstore.google.com/detail/meta-ray-ban-display-web/jpjlmmodokemlepklkdbimceggpbjcll) | Official browser QA tool; not physical proof. |

## Input, sensors, and physical interaction

| Source | Use |
| --- | --- |
| [Full Wearables reference](https://wearables.developer.meta.com/llms.txt?full=true) | Public v0.9 capability index that mentions native IMU sensors, Display UI/input, and the separate WebApps journey; use for discovery, not as proof of an importable native sensor symbol or physical behavior. |
| [DAT iOS Display Access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md) | Current public native Display view/action contract, `ButtonGroup`, tap callbacks, capability/teardown guidance, and sample boundary. |
| [DAT Android Display Access skill](https://github.com/facebook/meta-wearables-dat-android/blob/main/plugins/mwdat-android/skills/display-access/SKILL.md) | Android Display builder/input guidance; do not infer Kotlin symbols from iOS. |
| [Web Apps agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md) | Toolkit input model, D-pad/EMG focus activation, text/composer guidance, sensor skills, and simulator checks. |
| [Web Apps Display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md) | Additive 600x600 Display interaction model, captouch/Neural Band language, focus, gesture, text-entry, and accessibility guidance. |
| [Apple Core Motion](https://developer.apple.com/documentation/coremotion) | Explicit phone-local fallback for motion/orientation when the product permits it; not proof of glasses sensor access. |
| [Apple Core Location](https://developer.apple.com/documentation/corelocation) | Explicit phone-local location fallback and permission boundary; not proof of a Web App or native DAT geolocation API. |

The current public DAT iOS/Android repository trees reviewed on 2026-08-22 do
not expose a dedicated native IMU/EMG/temple sensor role or public package
surface in the same way that they expose Display, camera, MockDevice, and
debugging roles. The full-reference wording therefore remains a discovery
signal, and the exact native sensor API is `to-verify` until the selected API
reference/artifact and target build establish it. The Web Apps toolkit is more
specific, but its text/offline/back/gesture/sensor claims remain feature-level
source conflicts with the full-reference index and require simulator,
deployed-URL, firmware, and physical MRBD evidence.

## Consumer product context

| Source | Use |
| --- | --- |
| [Ray-Ban Meta (Gen 2) announcement](https://about.fb.com/news/2025/09/ray-ban-meta-gen-2-better-battery-life-video-capture/) | Consumer Gen 2 naming and launch context; not a DAT support matrix. |
| [Ray-Ban Meta Gen 2 announcement](https://about.fb.com/news/2026/05/ray-ban-meta-ai-glasses-launch-in-japan/) | Current consumer naming and Gen 2 context. |
| [Ray-Ban Meta Gen 2 and Optics announcement](https://about.fb.com/news/2026/03/meta-ai-glasses-built-for-prescriptions/) | Gen 2 Optics naming and product variants; not an SDK model mapping. |
| [Meta Glasses announcement](https://about.fb.com/news/2026/06/meta-essilorluxottica-partner-launch-meta-glasses/) | Current Meta Glasses product naming; not a direct DAT capability mapping. |
| [Meta Ray-Ban Display announcement](https://about.fb.com/news/2025/09/meta-ray-ban-display-ai-glasses-emg-wristband/) | Product/display context; do not infer third-party API behavior. |
