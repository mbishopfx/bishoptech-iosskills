# External Accessory setup and stream-trust design

External Accessory UI should make an MFi manufacturer boundary visible without overwhelming the person with protocol jargon. The app can feel native while still telling the truth about connected state, protocol support, stream readiness, and physical results.

This page covers connected MFi accessories and the optional MFi Wi-Fi configuration flow. It does not design generic BLE scanning or Apple Home control.

## Name the relationship clearly

Use a product-level explanation:

- “Connect your supported accessory to continue.”
- “This accessory supports the protocol needed for your selected feature.”
- “The accessory is connected, but its protocol is not ready.”
- “The app sent the command; the accessory has not confirmed the physical result.”

Avoid:

- “Bluetooth paired” when the route is MFi protocol communication;
- “Online” when only a cable/session exists;
- “Ready” before protocol and stream validation;
- “Done” when the app observed only a stream write.

## Choose the setup surface

| User situation | Surface | Ownership |
| --- | --- | --- |
| Accessory is already connected | App-owned accessory list/detail | App |
| Accessory connects/disconnects | App observes system notifications | System event plus app state |
| Protocol is not yet available | Waiting/authentication state | App explains; manufacturer/device completes |
| Unconfigured MFi Wi-Fi accessory | System-provided configuration UI | System |
| Stream is active | App-owned status/editor/control surface | App |
| Apple Home accessory | HomeKit surface and semantics | Home/system |
| Custom BLE accessory | Core Bluetooth/AccessorySetupKit route | Separate route |

Do not recreate the system-provided Wi-Fi configuration sheet. Let the system own setup, then return to an app-owned summary with the actual configuration status.

## Flow architecture

1. Start from a user outcome, not from a scan.
2. Explain the supported accessory and required protocol.
3. Read the current connected-accessory inventory.
4. Ask the person to choose the intended accessory when more than one is available.
5. Show manufacturer, model, firmware, and supported protocol only as useful context.
6. Check protocolStrings before attempting a session.
7. Open the session and show stream setup.
8. Display the exact feature that is available.
9. Require confirmation before a physical side effect.
10. Show result, freshness, retry, stop, and disconnect behavior.

For Wi-Fi configuration, add searching, system configuration, success/cancel/failure, and post-configuration protocol revalidation.

## State-driven UI

| State | Primary copy | Action |
| --- | --- | --- |
| No supported accessory | “Connect a supported accessory to begin.” | Setup help |
| Accessory connected | “Accessory connected.” | Choose/access details |
| Waiting for protocol | “Checking accessory authentication.” | Wait/cancel |
| Protocol unsupported | “This accessory cannot perform this feature.” | Choose another |
| Opening session | “Opening a secure feature session.” | Cancel |
| Streams opening | “Preparing accessory communication.” | Wait/cancel |
| Ready | “Ready for [feature].” | Continue |
| Input available | “New accessory update.” | Review/acknowledge |
| Output blocked | “Accessory is busy; trying again.” | Stop/retry |
| Disconnected | “Accessory disconnected.” | Reconnect/setup |
| Stale | “Last confirmed at [time].” | Refresh/reconnect |
| Unknown result | “The accessory has not confirmed the result.” | Check/retry |
| Removed | “This accessory is no longer connected.” | Forget/setup |

Use a visible freshness label for measurements, telemetry, and completed actions. Keep the date/time and uncertainty understandable at larger text sizes.

## Device identity without overclaiming

Show the manufacturer-supplied name and model as identification hints. Show the protocol compatibility and session state as technical status. Show a physical result only when the protocol reports it.

If the product has a manufacturer-approved authentication step, display:

- accessory selected;
- protocol supported;
- session opened;
- command accepted;
- device result confirmed.

These are separate checkpoints. A single green checkmark can hide too much.

## Stream and data surfaces

For an active stream:

1. show the latest decoded observation;
2. show the timestamp and unit;
3. show “updating,” “paused,” “stale,” or “disconnected”;
4. expose Stop or Close;
5. provide a bounded history only if it serves the user outcome;
6. hide raw frame counts and byte dumps behind diagnostics.

When an output stream is under pressure, the UI should communicate pause/retry rather than creating an infinite progress indicator. If a frame is malformed, show a recoverable error and retain a diagnostic code, not raw payload bytes.

## Liquid Glass application

Use Liquid Glass around functional groups:

- accessory summary and connection state;
- protocol-ready badge plus freshness;
- a compact command review group;
- a retry/stop action cluster.

Keep the primary measurement or editor content legible on a stable surface. Do not nest glass panels for every metadata row or make a stream look more reliable by adding translucency.

Use a material fallback when:

- Reduce Transparency is enabled;
- the device or target does not support the modifier;
- the content is high contrast or data dense;
- Dynamic Type makes a compact group unsuitable;
- VoiceOver needs a simpler semantic order.

## AI proposal design

An AI feature can translate a person’s phrase into a typed proposal:

person request -> accessory selection -> protocol capability -> proposal -> review -> session write -> accessory result

The proposal should show:

- the selected accessory;
- the intended operation;
- the value/unit;
- why the app thinks it applies;
- whether confirmation is required;
- what result can and cannot be confirmed.

Never show generated copy that implies an accessory acted when only an OutputStream accepted bytes. Keep a deterministic manual control available.

## Accessibility

Test the setup and stream workflows with:

- VoiceOver announcements for accessory name, model, protocol status, freshness, and error;
- Dynamic Type with long manufacturer/model names;
- Voice Control labels that distinguish duplicate accessory names;
- Switch Control reaching Choose, Configure, Confirm, Stop, Retry, Forget, and Close;
- Reduce Motion for searching/configuration transitions;
- Reduce Transparency and increased contrast;
- RTL and localization;
- keyboard/pointer focus where supported;
- Assistive Access or simplified mode if the target claims support.

Do not encode “connected” only with color, glow, or an animated waveform.

## Privacy and retention

Default to:

- no raw stream logging;
- no indefinite serial-number analytics;
- no raw protocol strings in model prompts;
- deletion-aware accessory records;
- typed command/result audit fields;
- clear disclosure when an accessory transmits a location, health, or other sensitive reading.

The manufacturer protocol may define data that the app must protect. Keep the app’s privacy policy, retention, and system surface copy aligned with that protocol.

## Review checklist

- [ ] The person understands why the accessory is needed.
- [ ] The app distinguishes connected, compatible, session-ready, and result-confirmed.
- [ ] System Wi-Fi configuration remains system-owned.
- [ ] The connected-accessory list is refreshed rather than blindly cached.
- [ ] Stream pressure and partial frames have visible recovery.
- [ ] Physical effects are confirmed by device results.
- [ ] AI proposals are typed and reviewable.
- [ ] Liquid Glass groups actions without hiding trust state.
- [ ] Accessibility works through setup, control, error, and removal.
- [ ] Evidence names the physical accessory, firmware, target, and platform.

## Sources

- [External Accessory](https://developer.apple.com/documentation/externalaccessory)
- [EAAccessoryManager](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager)
- [EAAccessory](https://developer.apple.com/documentation/externalaccessory/eaaccessory)
- [EASession](https://developer.apple.com/documentation/externalaccessory/easession)
- [EAAccessory protocol strings](https://developer.apple.com/documentation/externalaccessory/eaaccessory/protocolstrings)
- [Register for local accessory notifications](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/registerforlocalnotifications%28%29)
- [Connected accessories](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/connectedaccessories)
- [Wireless Accessory Configuration Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.external-accessory.wireless-configuration)
- [EAWiFiUnconfiguredAccessoryBrowser](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser)
- [Configure an unconfigured accessory](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/configureaccessory%28_%3Awithconfigurationuion%3A%29)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
