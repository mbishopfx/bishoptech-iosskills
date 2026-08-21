# Accessory discovery and pairing surfaces

Accessory setup is a trust ceremony. The person is about to give an app access to a nearby device, establish a connection, or authorize a physical action. The UI should make each transition legible:

    why this accessory
        -> what the system can see
        -> what the person selected
        -> what pairing authorizes
        -> what the app will do next
        -> how to remove or recover

Use Apple’s system picker and pairing surfaces wherever the framework provides them. Use custom SwiftUI and Liquid Glass for the surrounding explanation, configuration, status, and command review.

## Discovery is not trust

Design separate visual states for:

- candidate discovered;
- user selected;
- setup/pairing in progress;
- authorization accepted;
- transport connecting;
- protocol handshake accepted;
- connected;
- stale or disconnected;
- removed or revoked.

Avoid a single green “Connected” badge for all of those. A device can be visible but not selected, paired but not authenticated by the app protocol, connected but stale, or reachable but unable to perform the requested command.

## Add accessory entry point

The entry point should answer:

- What does adding an accessory enable?
- Which accessory types are supported?
- Does setup use Bluetooth, Wi-Fi, Wi-Fi Aware, or another route?
- Is setup user initiated?
- What permissions are handled by the system picker?
- What will happen after selection?
- How can the person remove or rename it later?

Good labels:

- “Add accessory”
- “Find nearby accessories”
- “Choose a controller”
- “Pair a second device”

Avoid:

- “Scan everything nearby”
- “Trust all devices”
- “Connect automatically” when a user selection and pairing confirmation are required
- “Secure” without explaining which system or protocol boundary provides security

Use a clear explanatory screen before showing the picker, then let the system own the actual discovery/authorization UI.

## AccessorySetupKit picker context

AccessorySetupKit’s system picker displays app-provided product names and images for matched descriptors. The app owns the quality of those assets:

- show the actual product category;
- use a recognizable product image with good contrast;
- use a name that distinguishes models or colors;
- avoid an icon that implies a different device;
- keep descriptors narrow enough that the user does not select an unrelated device.

If multiple devices match, the picker may show separate items. The app’s post-picker screen should show the selected accessory’s display name, supported transport, and the next setup step without implying that the app already authenticated the device’s physical owner.

Do not recreate the picker in SwiftUI. The system owns permission and setup. Your app can provide a “What happens next?” explanation and a reliable fallback if the picker fails or the device is unsupported.

## Pairing screen

For DeviceDiscoveryUI, the system picker is a full-screen pairing surface. The surrounding label should state:

- the app or device the person is connecting to;
- what data or controls will flow after pairing;
- whether the connection is temporary or permanent;
- what happens when the device is not supported;
- how to disconnect later.

If the route includes a PIN, make the publisher/subscriber roles obvious. Do not show an app-owned fake PIN sheet when the system owns the pairing exchange.

After the picker returns an endpoint:

1. Show “Selected” or “Pairing complete,” not “Trusted” unless app authentication also succeeded.
2. Start the transport connection.
3. Run a protocol version and capability handshake.
4. Present the device’s app-level authorization state.
5. Require confirmation before a high-impact command.

## Device detail screen

A good accessory detail screen is an inspector, not a dashboard full of decorative glass:

| Section | Content |
| --- | --- |
| Identity | User-visible name, product type, optional serial suffix if supported |
| Connection | Connected, connecting, stale, disconnected, last seen |
| Pairing | Temporary/permanent access, paired date, remove/forget |
| Protocol | Version, supported features, firmware/configuration state |
| Permissions | System authorization and app-level authorization |
| Commands | Only actions supported and safe for this device |
| Recovery | Reconnect, re-pair, update, support path |

Do not expose raw Bluetooth advertisement bytes, SSIDs, IP addresses, or opaque tokens as the main identity. Put technical details behind a diagnostics disclosure.

## Connection and command state

Use state labels that can be understood without color:

| State | UI copy | Control policy |
| --- | --- | --- |
| discovered | “Nearby” | Select/setup only |
| selected | “Selected” | Begin pairing or cancel |
| pairing | “Pairing…” | Disable duplicate pairing |
| authorized | “Authorized” | Start app protocol handshake |
| connecting | “Connecting…” | Allow cancel; show timeout |
| connected | “Connected” | Show supported commands |
| stale | “Last seen 12 seconds ago” | Disable risky command or require refresh |
| disconnected | “Not connected” | Reconnect or remove |
| protocolMismatch | “Update required” | Do not send commands |
| failed | “Couldn’t finish setup” | Explain retry/manual path |
| removed | “Accessory removed” | Add again |

Keep the state source visible in diagnostics: picker event, transport callback, protocol handshake, or last observation.

## Liquid Glass composition

Use Liquid Glass for functional grouping around app-owned content:

- an Add accessory action group;
- a device-status group;
- a command-review group;
- a settings/rename/remove group;
- a system-surface return banner.

Keep the system picker, pairing prompt, and accessory content visually clear. Do not blur or glass over a critical confirmation such as “Unlock door,” “Start motor,” “Erase device,” or “Update firmware.” Place the target, value, and consequence in a normal high-contrast content region and use a semantic destructive or confirmation control.

Glass should adapt when:

- Reduce Transparency is enabled;
- Reduce Motion is enabled;
- Dynamic Type grows;
- a product image is missing;
- the accessory is disconnected;
- the device is in dark mode or bright outdoor light;
- VoiceOver or Switch Control is active.

The effect is a hierarchy tool, not a substitute for trust text.

## DeviceDiscoveryUI surfaces

For DevicePicker:

- present the full-screen modal as the action’s main task;
- make the label a meaningful preflight description;
- make the fallback say which platform/feature is unsupported;
- do not put a permanent app-owned control behind the picker;
- handle cancellation without treating it as failure;
- record selection only after the callback returns an endpoint.

For DevicePairingView:

- provide a clear “make this device discoverable” action;
- explain who can connect;
- show the publisher’s current state;
- stop advertising when the user leaves the task or the app policy says so;
- use a protocol-level timeout and cancellation.

The user should know which device is publishing and which device is selecting. “Nearby device” is not enough when multiple products are in the room.

## Wi-Fi Aware design

Wi-Fi Aware has a service-oriented model. Design around the service:

- “Share video with the living-room display”
- “Control this app from your iPhone”
- “Send a file to the selected device”
- “Mirror workout controls to the TV”

Do not make “Wi-Fi Aware” the primary user-facing noun unless the user needs the technical detail. The person needs to know the service, target, and consequence.

Before DeviceDiscoveryUI:

1. Check WACapabilities support.
2. Confirm the target service is declared.
3. Provide a fallback when the device cannot pair.
4. Explain the connection is peer-to-peer and what data will flow.

After selection:

- show pairing progress;
- show the endpoint/connection state;
- negotiate protocol version;
- expose throughput/latency only in diagnostics or when it informs the task;
- show disconnected/stale state;
- provide a manual retry and device removal path.

## Accessibility and physical context

Pairing often occurs while a person is holding or moving a device. Test:

- large text and long product names;
- VoiceOver announcements for selected, pairing, connected, failed, and removed;
- Switch Control and Full Keyboard Access;
- high contrast and color filters;
- reduced motion/transparency;
- one-handed reach and safe button placement;
- bright light, gloves, and a noisy environment;
- multiple similar accessories nearby.

Every device row needs a label, role, current state, and action. A Bluetooth icon alone is not an accessible identity. An animated radar is not a status announcement.

## Privacy-forward copy

Prefer:

- “The system will show supported nearby accessories.”
- “You choose which device to add.”
- “The app will use this connection for the selected feature.”
- “Pairing does not automatically authorize every command.”
- “Remove this accessory to stop future connections.”
- “The selected device is not available right now.”

Avoid:

- “We can see every device near you.”
- “This device is safe because it is nearby.”
- “Connected means trusted.”
- “We know who owns this accessory.”
- “AI chose the best device for you.”

Use the [Accessory Design Guidelines](https://developer.apple.com/accessories/) and [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy) to keep the interaction transparent.

## AI review shell

AI can turn “send this to the TV in the kitchen” into a proposal, but the review must resolve:

- which device;
- which service;
- which content/data;
- which command;
- what happens if the device is stale;
- what permissions are required;
- whether the action is reversible.

Show:

    Proposal
    Target: Living-room display
    Service: File transfer
    Payload: 1 selected video
    Connection: paired, last seen 18 seconds ago
    Action: Send

The model should never choose a device from an ambiguous name, pass raw advertisement data into a prompt, or trigger an irreversible command without deterministic validation and user approval.

## Preview, fallback, and proof

Previews can show:

- add-accessory entry;
- empty/nearby/selected/paired/disconnected fixtures;
- report/status cards;
- command review;
- unsupported-platform fallback;
- accessibility identifiers.

They cannot prove:

- radio discovery;
- system picker matching;
- real pairing/PIN flow;
- physical-device ownership;
- Wi-Fi Aware support;
- endpoint encryption;
- accessory firmware/protocol compatibility;
- reconnect/thermal/battery behavior;
- safe physical side effects.

Use the [accessory and discovery proof matrix](../60-verification/23-accessory-setup-and-device-discovery-proof-matrix.md) for physical-device evidence.

## Sources

- [AccessorySetupKit](https://developer.apple.com/documentation/AccessorySetupKit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [Network](https://developer.apple.com/documentation/network)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Accessory Design Guidelines](https://developer.apple.com/accessories/)
