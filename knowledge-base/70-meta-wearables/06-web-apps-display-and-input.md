# Web Apps: display, input, and performance

Web Apps are the second first-class Meta Wearables route for Meta Ray-Ban
Display. They are ordinary HTML/CSS/JavaScript applications rendered on the
glasses display, not a native iOS target and not a substitute for DAT camera or
device-session access.

## Display contract

The official Web App toolkit currently describes:

| Constraint | Implementation consequence |
| --- | --- |
| `600x600` display viewport | Set the viewport metadata and design within a fixed canvas. Test text, safe zones, and overflow at the exact size. |
| Additive waveguide display | Black page background is transparent; visible UI surfaces need enough luminance and contrast to remain legible over the environment. |
| No touchscreen/cursor | Every action must be reachable through focus order and D-pad/EMG input. |
| D-pad navigation | Arrow keys move focus in the browser/simulator; Enter/pinch activates the focused control. |
| Public HTTPS URL for glasses delivery | A localhost server is a desktop smoke test, not on-device delivery. |
| Web runtime | Network, sensor, storage, text-composer, and offline behavior must be tested as Web App capabilities, not assumed from iOS APIs. |

## Source conflict ledger

Two official artifacts currently disagree on part of the Web App capability
contract:

| Official source | Current signal | Handling in this knowledge base |
| --- | --- | --- |
| [Developer Center full reference](https://wearables.developer.meta.com/llms.txt?full=true), reviewed 2026-08-22 | Lists Web Apps as having no camera, microphone, text input, offline support, notifications, or back navigation. | Use this as the conservative route-planning signal; do not assume any of those capabilities from ordinary browser behavior. |
| [Web App toolkit `main`](https://github.com/facebook/meta-wearables-webapp) at commit `a2714f862c61b1ce9c6cb624fc7e4938087102db`, including its current agent and performance guidance | Documents an on-glasses handwriting/voice composer for standard HTML fields, service-worker/offline patterns, Escape/back behavior, opt-in drag, and Generic Sensor API guidance. | Treat text composition, offline caching, back navigation, gesture extensions, and sensors as `source-conflict`/`to-verify` until the authenticated Developer Center or MCP result, simulator build, target firmware, and physical MRBD run agree. |

The toolkit is an official implementation aid, but its moving `main` branch is
not by itself a versioned glasses-firmware contract. Camera, microphone, and
notifications remain unsupported for this route in the current public index;
never infer browser access to them from the toolkit, a desktop browser, or a
nearby DAT capability.

Use the current identification metadata in the document head when targeting the
MRBD route:

```html
<meta name="viewport" content="width=600, height=600, initial-scale=1.0">
<meta name="mrbd-web-app-capable" content="yes">
```

Keep the exact `content="yes"` value where the official toolkit requires it.

## Interaction rules

- Put all actionable elements in a deterministic focus order.
- Give focus a visible, high-contrast treatment; do not rely on a mouse hover.
- Keep pinch as activation of the focused element. Continuous drag is an
  explicit opt-in route, not a default cursor.
- Make loading, offline, stale, error, and empty states reachable with the same
  D-pad path as the happy path.
- Keep screens short and scannable; use sequential cards or views rather than a
  dense phone-style dashboard.
- If text input is needed, the toolkit’s HTML-field composer is a candidate
  route, but its support is currently source-conflicted. Keep a paired-phone or
  manual-entry fallback until the exact target proves the composer.
- Treat Escape/back behavior, offline cache use, sensor access, and extended
  gestures the same way: implement a recoverable fallback and label the feature
  `to-verify` until the target route proves it.

## Sensor and API boundaries

The Web App toolkit documents browser-style APIs and sensor skills, but an
available browser API does not prove a particular glasses firmware exposes it.
Record the API, permission, runtime, network, source-conflict status, and device
evidence separately. Do not call a source-conflict feature on-device compliant
until the target-specific run closes the conflict.
Use the [input, sensors, and physical interaction route](24-input-sensors-and-physical-interaction.md)
for the normalized event/epoch contract, phone fallback, teardown, privacy,
and named-target evidence rows.
For remote data:

```text
fetch/WebSocket
  -> timeout/cancellation/retry
  -> schema validation and freshness check
  -> bounded display projection
```

Keep API keys server-side, avoid putting personal data into URLs, and do not
let remote content create an unsafe or unreviewed action. For offline flows,
cache only the data that the product can safely use when stale.

## Simulator and deployment

The official toolkit describes a Chrome extension that recreates the 600x600
surface, additive blending, environment backgrounds, D-pad input, display
tuning, recording, and QA checks. Use it for layout/focus regression and bug
reports. Then deploy to a stable public HTTPS URL and test the add-to-glasses
flow through the Meta AI app. Exercise text composition, offline behavior,
back/exit, sensors, and gestures as separate feature rows because the current
Developer Center index and toolkit `main` disagree about several of them.
Neither step substitutes for a physical Display/Neural Band task on the exact
build and firmware.

## Sources

- [Official Meta Wearables Web App toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Web App display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Web App performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md)
- [Web App agent instructions](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Meta Wearables Web Apps documentation](https://wearables.developer.meta.com/docs/develop/webapps)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
- [Meta Wearables MCP server](https://mcp.developer.meta.com/wearables)
- [Meta Ray-Ban Display Web App Simulator](https://chromewebstore.google.com/detail/meta-ray-ban-display-web/jpjlmmodokemlepklkdbimceggpbjcll)
