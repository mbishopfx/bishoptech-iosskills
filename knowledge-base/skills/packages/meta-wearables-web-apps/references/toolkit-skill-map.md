# Web Apps toolkit skill map

The official Web Apps toolkit `main` snapshot reviewed 2026-08-30 was
`a2714f862c61b1ce9c6cb624fc7e4938087102db`; its Codex plugin reports version
`127.0.0`. Use this as a route map, not as proof that every feature is exposed
by every deployed glasses runtime.

| Toolkit skill | Use | Local evidence handoff |
| --- | --- | --- |
| `create-webapp` | Scaffold `index.html`, `styles.css`, `app.js`, metadata, favicon, and 600×600 verification. | `browser-sim` then `physical` Web App task. |
| `add-ui` | Focusable screens, buttons, lists, cards, forms, toggles, counters, and navigation. | Display/input fixture. |
| `add-text-input` | Standard HTML fields and on-glasses handwriting/voice composer. | `source-conflict`/`to-verify`; phone/manual fallback. |
| `add-gestures` | Pinch activation and page-level opt-in continuous drag. | `source-conflict`/`to-verify`; physical EMG task. |
| `add-device-sensors` | Generic Sensor API and geolocation. | Permission/runtime/device `to-verify`; stop sensors offscreen. |
| `add-local-storage` | `localStorage`/`sessionStorage` persistence. | Browser/physical storage row; do not store secrets or raw media. |
| `add-offline` | Service Worker/Cache API app-shell and offline UI. | `source-conflict`/`to-verify`; stale-data fallback. |
| `connect-api` | REST/WebSocket data with loading/error/freshness handling. | Public URL/privacy/network evidence. |
| `test-on-device` | Vercel staging URL, no-login access, QR/manual add flow, live iteration. | Hosted URL plus physical Display proof. |
| `publish-to-vercel` | Stable production HTTPS URL and add-to-glasses instructions. | Publishing/URL evidence, not App Store proof. |
| `passcode-for-testing` | Optional temporary three-digit test gate. | Security/privacy review; never rely on it for production. |
| `qr-code` | Local QR generation for a URL or short payload. | Convenience artifact only. |

## Toolkit-wide rules worth carrying locally

- Require the viewport, `meta description`, and
  `mrbd-web-app-capable=yes` metadata.
- Keep the additive page background black, UI surfaces dark gray, safe zone at
  8dp, interactive targets at 88dp, and text scalable.
- Treat focus/Enter/Escape and input/change events as explicit interaction
  contracts; do not depend on a mouse or positioned cursor.
- Target <3s load, <500KB gzipped JavaScript, 60fps, <128MB memory, and <10
  initial requests; stop sensors/animation when not needed.
- Public HTTPS is required for glasses delivery. Localhost is only a desktop
  smoke test; staging and production URLs are separate evidence rows.

## Open source conflict

The full Developer Center index currently lists no text input, offline support,
or back navigation, while this toolkit snapshot documents those routes plus
extended gestures and sensors. Preserve both source observations. Do not make a
conflicted feature a release requirement until authenticated docs/MCP, the
simulator/build, the target firmware, and the physical MRBD run agree.

## Sources

- [Web Apps toolkit](https://github.com/facebook/meta-wearables-webapp)
- [Web Apps Codex plugin](https://github.com/facebook/meta-wearables-webapp/tree/main/plugins/meta-wearables-webapp)
- [Web Apps agent guidance](https://github.com/facebook/meta-wearables-webapp/blob/main/AGENTS.md)
- [Web App display guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/display-guidelines.md)
- [Web App performance guidelines](https://github.com/facebook/meta-wearables-webapp/blob/main/plugins/meta-wearables-webapp/references/performance-guidelines.md)
- [Full Wearables platform reference](https://wearables.developer.meta.com/llms.txt?full=true)
