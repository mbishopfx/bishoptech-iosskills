# Upstream DAT skill and tooling map

The official `facebook/meta-wearables-dat-ios` repository publishes more than
SDK prose. It is also a versioned agent/tooling knowledge base. Use this page to
route an implementation or debugging task to the upstream source without
copying the upstream instructions wholesale into this repository.

## Upstream iOS roles

| Upstream skill | Use it for | Local Meta role/handoff |
| --- | --- | --- |
| `getting-started` | SPM, target modules, Info.plist, `Wearables.configure()`, callback, registration, first stream | `meta-dat-ios-integration` |
| `permissions-registration` | Meta AI registration, callback, DAT camera permission, multi-device permission behavior, Developer Mode/release channels | `meta-dat-ios-integration` + privacy |
| `dat-conventions` | module names, Swift naming, entrypoint/types, async patterns, build/test commands, MCP/docs search | `meta-dat-api-atlas` |
| `camera-streaming` | `Camera`, `Stream`, `StreamConfiguration`, video/photo publishers, quality/backpressure | `meta-dat-camera-audio` |
| `display-access` | Display capability, DSL, buttons/icons/images/video, input, link/setup and error gates | `meta-dat-display` |
| `session-lifecycle` | device-driven session/stream states, pause/resume, availability and teardown | `meta-dat-ios-integration` + device proof |
| `mockdevice-testing` | simulated registration/permissions/devices/media/gestures and XCUITest test server | `meta-wearables-device-proof` |
| `debugging` | Developer Mode, compatibility, state diagnosis, logs, known issues | `meta-dat-api-atlas` + device proof |
| `live-debugging-mcp` | read-only live DAT Inspector/debug-server diagnosis and redacted diagnostic bundle | `meta-dat-api-atlas` + device proof |
| `sample-app-guide` | complete CameraAccess-style SwiftUI target architecture and allowed dependencies | `meta-dat-api-atlas` + iOS Apple roles |

The repo also contains root `AGENTS.md`, Copilot/Cursor surfaces, plugin
metadata, and sample apps. Check the upstream commit before treating a role or
file path as current.

## Release-anchored source-tree inventory

The portable [surface manifest](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
and [source-tree checker](../skills/packages/meta-wearables-source-refresh/scripts/check_source_tree_inventory.py)
keep the repository-level inventory explicit:

| Lane | Inventory anchors at the reviewed revision |
| --- | --- |
| iOS | Five 0.9.0 Package.swift products/five XCFrameworks, the exact ten-role set recorded in the manifest, `CameraAccess` and `DisplayAccess`, plugin version 0.9.0, and DisplayAccess prerequisites iOS 17.2+/Xcode 26.4+/Swift 6.3+. |
| Android | The exact ten-role set recorded in the manifest, `CameraAccess` and `DisplayAccess`, plugin version 0.9.0, four 0.9.0 Maven artifacts, and sample min/compile/target SDK 31/36/36. |
| Web Apps | The exact twelve-role set recorded in the manifest, plugin version 127.0.0, `display-guidelines.md`/`performance-guidelines.md`, the `snake` example, and `templates/prompts.json`. |

These are source-tree anchors, not generated API, target compilation, account,
named-device, physical, or release evidence. The same checker also verifies the
agent-facing root files and lane plugin manifests below; a plugin manifest or
MCP endpoint proves source/tool routing only. Run the checker after the public
ref checker whenever a role, sample, package, artifact, or toolkit asset is used
to justify a full-SDK claim.

## AI-compatible root surfaces

The three official repositories expose a common agent-facing root contract at
the pinned revisions:

| Lane | Root files | Plugin metadata | Docs route |
| --- | --- | --- | --- |
| DAT iOS | `AGENTS.md`, `README.md`, `install-skills.sh` | `plugins/mwdat-ios/.codex-plugin/plugin.json` | `https://mcp.developer.meta.com/wearables` |
| DAT Android | `AGENTS.md`, `README.md`, `install-skills.sh` | `plugins/mwdat-android/.codex-plugin/plugin.json` | `https://mcp.developer.meta.com/wearables` |
| Web Apps | `AGENTS.md`, `README.md`, `install-skills.sh` | `plugins/meta-wearables-webapp/.codex-plugin/plugin.json` | `https://mcp.developer.meta.com/wearables` |

These files are deliberately inventoried as upstream AI/tooling inputs. They
help the local team discover current role instructions, install surfaces, and
documentation lookup routes; they do not prove a target build, authenticated
Developer Center state, device pairing, physical glasses behavior, or release
eligibility.

## Agent/tool routes

### Static API context

Use the current [full `llms.txt` endpoint](https://wearables.developer.meta.com/llms.txt?full=true)
when the client needs a broad static reference. It names the DAT and Web Apps
product journeys, current guides, API references, hardware/version pages,
MockDevice, release channels, and tool integrations. Record the retrieval date
because the endpoint is living documentation.

### Live docs MCP

The official public MCP endpoint is:

```text
https://mcp.developer.meta.com/wearables
```

The upstream conventions/debugging guidance names `search_dat_docs` for current
DAT lookup. The upstream README says this public docs server does not require
authentication; do not add tokens, OAuth, or custom authorization headers. The
same server has `search_webapps_docs` for the distinct Web Apps route. A live
MCP result is source lookup, not a build, device, account, or physical proof.

For Web Apps, compare `search_webapps_docs` and the full `llms.txt` index with
the official toolkit `main` snapshot (`a2714f862c61b1ce9c6cb624fc7e4938087102db`).
The reviewed toolkit documents text composition, offline/service-worker,
Escape/back, gesture, and sensor routes that the full index currently lists as
unsupported or does not expose. Preserve the conflict as
`source-conflict`/`to-verify` and let the simulator/physical packet close it.

### Local live-debugging MCP

If a project exposes a local DAT Inspector/debug server, use the upstream
`live-debugging-mcp` loop:

1. discover/connect the debug server;
2. establish connection, SDK, and DAT readiness;
3. inspect companion boundary, device path, permissions, and properties;
4. ask for a narrow reproduction;
5. wait for categorized events/errors;
6. export a redacted diagnostic bundle.

Keep this read-only unless the user explicitly authorizes an app change. It
diagnoses app-visible DAT events; it is not introspection into Meta AI internals
and it does not grant permission to mutate the account, device, or release
channel.

### Codex/plugin route

The official DAT repositories ship Codex plugin payloads under their lane
plugin directories. Their READMEs document the local install commands
`codex plugin install ./plugins/mwdat-ios` and
`codex plugin install ./plugins/mwdat-android`, plus the corresponding
`./install-skills.sh codex` helper. The Web Apps README uses the marketplace
route (`codex plugin marketplace add ...`, then `/plugins` in Codex) and an
`install-skills.sh all` fallback. The local [agent-surface contract](../skills/packages/meta-wearables-full-sdk-audit/references/surface-manifest.yaml)
keeps those routes explicit so a native DAT plugin is not mistaken for a Web
Apps plugin or for an SDK runtime.

All three official READMEs point to the shared public Wearables MCP. The DAT
lookup tool is `search_dat_docs`; the Web Apps lookup tool is
`search_webapps_docs`; the official README states that the server requires no
auth, OAuth, token, or custom authorization header. This workspace currently
marks MCP as not locally callable, so use the pinned repository/full-reference
fallback and keep every lookup at `source` evidence.

This workspace keeps a synthesized, portable package so its role boundaries and
Apple evidence vocabulary remain stable; use the upstream plugin as a
versioned source/refresh input, not as an unreviewed replacement.

## Sample-app route

The official CameraAccess and DisplayAccess samples provide a concrete source
map:

```text
App entry/configuration
  -> WearablesViewModel (registration/devices)
  -> feature ViewModel (session/camera/display)
  -> SwiftUI view/projection
  -> MockDevice debug/test surface
```

The current sample setup uses `MWDATCore` always, `MWDATCamera` for camera,
`MWDATDisplay` for native Display, and `MWDATMockDevice` for debug/test work.
Review the sample’s `Info.plist`, target membership, listener-token lifetime,
background behavior, and stop order rather than copying its UI or configuration
blindly.

## Version and evidence rules

- Upstream prose can lag a release: the current repo’s older getting-started
  prerequisite text says iOS 16, while the 0.9.0 changelog says iOS 17.2.
- A repository sample can show a viable route but does not prove a different
  target, account, firmware, release channel, or physical model.
- MCP/docs search proves a source lookup; MockDevice proves controlled logic;
  browser simulation proves Web App behavior; only the named physical device
  proves glasses rendering/audio/input for the exact script.
- The public product map currently separates DAT (native mobile) and Web Apps
  (MRBD Display). The current raw full reference is labeled DAT SDK v0.9; the
  separate Web Apps toolkit/Developer Center sources own the hosted route.
  “Regular SDK” is not a third public native iOS product in the reviewed
  source; resolve it to one of those routes or keep it `to-verify`.
- The Web Apps toolkit `main` and full-reference index are not currently a
  single consistent capability contract. Do not present toolkit guidance as
  firmware support without target evidence.

## Sources

- [DAT iOS repository](https://github.com/facebook/meta-wearables-dat-ios)
- [DAT iOS README and AI-assisted development](https://github.com/facebook/meta-wearables-dat-ios#readme)
- [DAT iOS plugin skills](https://github.com/facebook/meta-wearables-dat-ios/tree/main/plugins/mwdat-ios/skills)
- [DAT iOS samples](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Wearables MCP endpoint](https://mcp.developer.meta.com/wearables)
- [Web Apps repository](https://github.com/facebook/meta-wearables-webapp)
