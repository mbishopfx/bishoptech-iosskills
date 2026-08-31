# Public Meta Wearables plugin and skill matrix

This page maps the repository-native agent surfaces that Meta currently ships
alongside DAT iOS, DAT Android, and Web Apps. It is the source map for the
local specialist team; it is not a wholesale copy of any upstream skill.
Reviewed 2026-08-30 against the current public refs; DAT iOS/Android detail
rows retain their 2026-08-22 source review dates:

| Surface | Revision observed | Public plugin identity |
| --- | --- | --- |
| DAT iOS | `main` `225f64ff1617e7acc8c407bb8d3ee132f7263d00`; reproducible `0.9.0` tag `9b1b83d791dfebff7afd452e924a256819094b64` | `mwdat-ios`, plugin version `0.9.0` |
| DAT Android | `main` `81dfb51b9be26de5cd262bb1dcbb4b8d0d6bd2bc` | `mwdat-android`, plugin version `0.9.0` |
| Web Apps | `main` `a2714f862c61b1ce9c6cb624fc7e4938087102db` | `meta-wearables-webapp`, plugin version `127.0.0` |

Pin the DAT tag or Maven artifact used by a real target. Treat repository
`main` and the Web Apps toolkit version as refresh inputs, not as a runtime or
firmware guarantee.

The upstream repositories also expose an agent-facing root surface:
`AGENTS.md`, `README.md`, `install-skills.sh`, each lane’s
`.codex-plugin/plugin.json`, and the public [Wearables MCP](https://mcp.developer.meta.com/wearables).
The official READMEs document local Codex plugin installs for native DAT,
marketplace installation for Web Apps, and the shared no-auth MCP lookup route
(`search_dat_docs` or `search_webapps_docs`). The local source-tree checker and
the machine-readable agent-surface contract inventory those paths and install
modes alongside the role names. They improve source discovery and handoff
routing; they are not SDK compile, account, device, physical, or release
evidence.

## DAT iOS repository-native roles

The official iOS plugin publishes ten role skills under
`plugins/mwdat-ios/skills/`:

| Upstream role | Local handoff | Use |
| --- | --- | --- |
| `getting-started` | `meta-dat-ios-integration` | Swift Package Manager, modules, target configuration, initialization, callback, and first route. |
| `permissions-registration` | `meta-dat-ios-integration` + privacy | Meta AI registration, permissions, Developer Mode, and release-channel conditions. |
| `camera-streaming` | `meta-dat-camera-audio` | Camera, stream, frame/photo publishers, configuration, and backpressure. |
| `display-access` | `meta-dat-display` | Native Display capability, content DSL, input, video, and link gates. |
| `session-lifecycle` | `meta-dat-ios-integration` + device proof | Session/stream state, pause, availability, and teardown. |
| `mockdevice-testing` | `meta-wearables-device-proof` | Deterministic device, permission, media, and UI-test control. |
| `debugging` | `meta-dat-api-atlas` + device proof | Developer Mode, compatibility, logs, and typed diagnosis. |
| `live-debugging-mcp` | `meta-dat-api-atlas` + device proof | Read-only DAT Inspector/debug-server diagnosis and redacted bundles. |
| `dat-conventions` | `meta-dat-api-atlas` | Naming, async patterns, source search, build/test conventions, and MCP use. |
| `sample-app-guide` | `meta-dat-api-atlas` + Apple roles | CameraAccess/DisplayAccess target shape and sample configuration review. |

The local roles synthesize these routes with Apple privacy, concurrency,
accessibility, and release evidence. The upstream plugin remains the exact
versioned source to reopen when a symbol or command matters.

The machine-readable source inventory records these ten names in exact sorted
order and the live source-tree checker compares the upstream directory names,
not only the role count.

## DAT Android repository-native roles

The Android plugin mirrors the same ten conceptual roles under
`plugins/mwdat-android/skills/`, but Kotlin, Gradle, Manifest, `Flow`/
`StateFlow`, and `DatResult` are distinct contracts. The local
`meta-dat-android-integration` role owns this route. It must not infer Swift
signatures, iOS Info.plist keys, or iOS evidence from Android parity.

The public 0.9.0 Android artifacts are:

```text
com.meta.wearable:mwdat-core:0.9.0
com.meta.wearable:mwdat-camera:0.9.0
com.meta.wearable:mwdat-display:0.9.0
com.meta.wearable:mwdat-mockdevice:0.9.0
```

The repository uses GitHub Packages and documents a `read:packages` token
through `GITHUB_TOKEN` or local Gradle properties. Never print, commit, or
embed that token in a knowledge-base page, fixture, archive, or build log.

The local [`meta-dat-android-api-atlas`](../skills/packages/meta-dat-android-api-atlas/SKILL.md)
role is the Android counterpart to the iOS API atlas. It owns exact Maven
artifact/symbol mapping, the 0.9 camera/Display/`DatResult`/DAM/R8 migration
ledger, Android `Session`/`DeviceSession` source conflict, Java interop, and
Android-specific compile/mock/physical evidence boundaries. It does not infer
Kotlin symbols from Swift or call the Android phone-microphone sample a glasses
HFP result.

## Web Apps repository-native roles

The current Web Apps plugin publishes these focused skills:

| Upstream skill | Local handoff | Primary output |
| --- | --- | --- |
| `create-webapp` | `meta-wearables-web-apps` | 600×600 scaffold, metadata, focusable UI, favicon, and verification checklist. |
| `add-ui` | `meta-wearables-web-apps` + Display | Screens, buttons, lists, forms, cards, navigation, and focus states. |
| `add-text-input` | Web Apps + device proof | Standard-field composer route, committed `input`/`change` values, and fallback. |
| `add-gestures` | Web Apps + device proof | Pinch activation and opt-in continuous drag. |
| `add-device-sensors` | Web Apps + privacy | Generic Sensor API and geolocation route with permission/device checks. |
| `add-local-storage` | Web Apps + privacy | Bounded `localStorage`/`sessionStorage` persistence. |
| `add-offline` | Web Apps + device proof | Service Worker/Cache API app shell and offline UI. |
| `connect-api` | Web Apps + privacy | REST/WebSocket data, timeout, freshness, and error states. |
| `test-on-device` | Device proof | Public staging HTTPS URL and physical glasses test loop. |
| `publish-to-vercel` | Privacy/publishing + device proof | Stable public HTTPS deployment, not App Store delivery. |
| `passcode-for-testing` | Privacy/publishing | Optional temporary testing gate; not a substitute for deployment security. |
| `qr-code` | Device proof | Local QR artifact for adding a hosted URL; QR scanning is not physical proof. |

The toolkit also ships display/performance references, templates, a favicon
script, and a public MCP route using `search_webapps_docs`. Its current `main`
guidance documents several features that conflict with the full Developer
Center index; the local team keeps those features `source-conflict`/
`to-verify` until the exact runtime is exercised.

The exact twelve-role list is source-pinned in the manifest and checked against
the upstream plugin directory on every source-tree refresh.

## Local cross-cutting compliance role

The upstream repositories do not publish one single “on-device compliance”
role. The local [`meta-wearables-on-device-compliance`](../skills/packages/meta-wearables-on-device-compliance/SKILL.md)
package composes the upstream DAT/Web Apps facts with the workspace privacy,
thermal, lifecycle, storage, network, fallback, and evidence contract. It
classifies processing as `glasses-native`, `phone-local`, `remote`, `mixed`, or
`unknown`; it does not add a new Meta SDK or imply that a phone companion is
glasses-native.

The local [`meta-wearables-operational-readiness`](../skills/packages/meta-wearables-operational-readiness/SKILL.md)
package owns the cross-surface reliability layer that upstream roles leave
distributed: the companion/firmware/on-glasses-DAT-app tuple, Developer Mode
versus release-channel behavior, version-dependency conflicts, update-required
and device-unavailable diagnosis, thermal/power stop behavior, bounded recovery,
and redacted operational evidence. It does not convert a repository issue or a
successful recovery attempt into an official support guarantee.

The local [`meta-wearables-app-architecture`](../skills/packages/meta-wearables-app-architecture/SKILL.md)
package owns the implementation boundary that upstream role skills assume but
do not define as one contract: shared product state and policy, iOS/Android
adapters, native Display/Web App presenters, phone fallback, session epochs,
resource ownership, bounded media queues, stale-event rejection, and layered
reducer/fake/mock/browser/physical test seams. It does not add a cross-platform
SDK or erase platform-specific API and lifecycle differences.

The local [`meta-wearables-developer-operations`](../skills/packages/meta-wearables-developer-operations/SKILL.md)
package owns the administrative layer surfaced by the full reference: MMA and
Wearables team boundaries, projects, platform app identities, product listings,
permission justifications, integration versions, DAT build readiness, invite-only
channels, tester Meta Accounts, Meta AI channel state, telemetry, and bounded
account recovery. It does not mutate an external account without explicit live
authorization or convert channel access into physical-device proof.

The local [`meta-wearables-security-attestation`](../skills/packages/meta-wearables-security-attestation/SKILL.md)
package owns the security boundary that crosses those administrative and mobile
integration roles: iOS/Android identity tuples, Meta AI callback ownership and
stale/duplicate handling, Developer Mode versus release attestation, GitHub
Packages and signing credential redaction, Web App origin/client exposure,
privacy-manifest/App Store gates, processing-location handoff, and `SEC-*`
evidence. It does not claim account access, credential validity, physical
capability, local processing, or store approval from source/configuration alone.

The local [`meta-wearables-transport-reliability`](../skills/packages/meta-wearables-transport-reliability/SKILL.md)
package owns the transport layer that cuts across the upstream camera, audio,
session, Display, and debugging roles: Bluetooth control, iOS Wi-Fi/local-network
and Bonjour configuration, Android Bluetooth/Internet/artifact parity, HFP/A2DP
route state, bounded queues, route changes, thermal/power, disconnect, and
recovery. It keeps iOS's explicit Wi-Fi signal separate from Android's unresolved
DAT Wi-Fi parity and never turns a declared permission into physical proof.

The local [`meta-wearables-debugging-observability`](../skills/packages/meta-wearables-debugging-observability/SKILL.md)
package makes the upstream `debugging` and `live-debugging-mcp` roles
first-class. It owns the read-only debug-server connection/readiness baseline,
companion-boundary and device-path diagnosis, narrow event/error evidence,
platform-specific failure mapping, and redacted diagnostic handoff. It does
not mutate external state or turn app-visible debug events into physical or
release proof.

The local [`meta-wearables-input-sensors`](../skills/packages/meta-wearables-input-sensors/SKILL.md)
package owns the cross-surface input/sensor contract that upstream roles leave
distributed: native Display callbacks, Web App D-pad/EMG/temple guidance,
browser motion/orientation/geolocation, phone sensor fallbacks, permission and
secure-context gates, event epochs, listener teardown, sampling/privacy, and
physical input/sensor evidence. It does not turn a Web App toolkit skill into a
native DAT sensor API.

## Route resolution for “regular SDK”

“Regular SDK” is not a third public native iOS product in the reviewed source.
Resolve the phrase explicitly:

| Intended outcome | Route |
| --- | --- |
| iOS companion app registers, selects devices, captures camera/media, or owns a native Display session | DAT iOS + native Apple target. |
| Android companion app uses the same product family | DAT Android + Gradle/Manifest target. |
| HTML/CSS/JavaScript experience is delivered to Meta Ray-Ban Display | Web Apps hosted HTTPS route. |
| User means Meta AI companion-app registration or consumer voice behavior | Meta AI/account surface; do not invent a third-party SDK permission or API. |

DAT, native Display, and Web Apps have separate lifecycle, privacy, publishing,
and evidence gates. A source lookup or plugin install does not prove a target
build, account, device generation, physical input, or release eligibility.

## Agent handoff sequence

1. Record route, exact repository/artifact revision, target platform, device
   wording, and requested capability.
2. Read the matching upstream role and local route page; preserve any source
   conflict instead of choosing the more convenient wording.
3. Produce a compatibility/configuration/privacy contract before code.
4. Add deterministic mock/simulator cases and a phone fallback.
5. Run the named physical/system task only when the target, account, and
   hardware are available; record the exact evidence label.
6. Repackage the local role only after source, link, archive, and privacy checks.

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS Codex plugin](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios)
- [DAT Android repository](https://github.com/facebook/meta-wearables-dat-android)
- [DAT Android Codex plugin](https://github.com/facebook/meta-wearables-dat-android/tree/main/plugins/mwdat-android)
- [Web Apps repository](https://github.com/facebook/meta-wearables-webapp)
- [Web Apps Codex plugin](https://github.com/facebook/meta-wearables-webapp/tree/main/plugins/meta-wearables-webapp)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables MCP](https://mcp.developer.meta.com/wearables)
