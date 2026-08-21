# AccessorySetupKit, DeviceDiscoveryUI, and Wi-Fi Aware

Apple now provides distinct system routes for onboarding accessories and pairing apps or devices:

- AccessorySetupKit discovers and configures Bluetooth or Wi-Fi accessories through a privacy-preserving system picker.
- DeviceDiscoveryUI presents pairing for apps to apps or apps to devices over secure peer-to-peer connections.
- Wi-Fi Aware provides the peer-to-peer service, browser, listener, pairing, and data-path machinery for supported devices.
- Core Bluetooth, Network, HomeKit, and Nearby Interaction remain separate choices for the post-setup transport or a different product capability.

The architecture should preserve the boundary:

    user goal
        -> route selection
        -> system discovery/pairing UI
        -> selected device/accessory
        -> authorization and trust
        -> transport connection
        -> versioned protocol
        -> bounded command or data flow
        -> disconnect/revoke/recovery

Discovery is not identity. Pairing is not application authorization. A connected endpoint is not proof that a physical action is safe.

## Capability map

| User outcome | Primary Apple route | Result | Separate next step |
| --- | --- | --- | --- |
| Let a person add a known Bluetooth accessory | AccessorySetupKit | ASAccessorySession and selected ASAccessory | Core Bluetooth or another supported accessory transport |
| Let a person add a Wi-Fi accessory | AccessorySetupKit | Selected accessory and setup authorization | Wi-Fi or product protocol connection |
| Add a custom accessory with filtering | AccessorySetupKit with picker filtering | ASDiscoveredAccessory and custom display item | Validate authenticity and pair/configure |
| Migrate an existing accessory integration | AccessorySetupKit migration items | Previously known peripheral/SSID recognized by the picker | Wait for migration completion before Core Bluetooth work |
| Pair two app instances or an app and device | DeviceDiscoveryUI | Selected NWEndpoint or provider endpoint | Network listener/connection and app protocol |
| Pair over Wi-Fi Aware | DeviceDiscoveryUI + Wi-Fi Aware | Secure paired device and Network path | WAPublisherListener or WASubscriberBrowser |
| Measure distance to a supported peer | Nearby Interaction | NISession range/direction | Separate token exchange and physical proof |
| Read/control a Home accessory | HomeKit | HomeKit accessory/characteristic state | Home authorization and physical side-effect confirmation |
| Talk to a custom BLE protocol after setup | Core Bluetooth | CBCentralManager/CBPeripheral | GATT schema, reconnect, background and hardware proof |

Apple’s [AccessorySetupKit overview](https://developer.apple.com/documentation/AccessorySetupKit) describes privacy-preserving discovery and configuration of Bluetooth or Wi-Fi accessories. The [DeviceDiscoveryUI overview](https://developer.apple.com/documentation/devicediscoveryui) describes app-to-app and app-to-device pairing over secure peer-to-peer networks and distinguishes it from AccessorySetupKit.

## AccessorySetupKit

### What the system owns

AccessorySetupKit is designed to let a person discover and select supported accessories without granting the app overly broad Bluetooth or Wi-Fi access during setup. The app describes what it supports, presents an OS-owned picker, receives the selected accessory event, and then uses the selected accessory information to create a product connection.

The setup route is:

    Info.plist accessory declarations
        -> ASAccessorySession.activate
        -> ASPickerDisplayItem / ASDiscoveryDescriptor
        -> system accessory picker
        -> ASAccessoryEvent.accessoryAdded
        -> picker dismissal
        -> app-owned configuration screen
        -> transport connection

The picker is user-initiated. Apple’s AccessorySetupKit guidance recommends giving the person enough context before showing it and binding it to a clear action such as Add accessory.

### Info.plist is part of discovery

The current AccessorySetupKit information-property-list route uses NSAccessorySetupSupports for Bluetooth and/or WiFi. Bluetooth discovery also requires the supported company identifiers, names, and services declared in the app’s information property list. The descriptor values used by the picker need to match those declarations; an invalid or incomplete declaration can prevent discovery or cause a failure.

Keep a source and built-Info register:

- wireless technologies used;
- Bluetooth company identifiers;
- Bluetooth names or substrings;
- Bluetooth service UUIDs;
- Wi-Fi SSID or prefix policy;
- Wi-Fi Aware descriptor if applicable;
- target and extension membership;
- current SDK spelling and availability.

Do not put an arbitrary broad vendor list in the plist to make discovery “work.” Scope it to the accessories the app can actually configure.

See [NSAccessorySetupSupports](https://developer.apple.com/documentation/bundleresources/information-property-list/nsaccessorysetupsupports) and the [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories) guide.

### ASAccessorySession lifecycle

ASAccessorySession is the coordination object. Activate it on a deliberate queue and handle event types such as:

- activated;
- accessoryAdded;
- accessoryChanged;
- accessoryRemoved;
- invalidated;
- accessoryDiscovered;
- pickerDidPresent;
- pickerDidDismiss;
- pickerSetupBridging;
- pickerSetupPairing;
- pickerSetupFailed;
- pickerSetupRename;
- migrationComplete;
- unknown.

The event handler is the lifecycle authority for the discovery session. The selected accessory may arrive before the picker dismisses. If the app presents its own configuration UI, retain the accessory reference and wait for pickerDidDismiss before changing the app surface.

When the session is invalidated, stop using it and create a new session only after the product has a clear recovery reason. Do not keep presenting a picker from a dead session.

Use [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession) and [ASAccessoryEventType](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryeventtype) for current event and lifecycle names.

### Discovery descriptors

ASDiscoveryDescriptor identifies accessories for picker matching. A Bluetooth descriptor can use a service UUID or company identifier, then refine with:

- Bluetooth name substring;
- manufacturer data blob and mask;
- service data blob and mask;
- immediate Bluetooth range;
- supported options.

A Wi-Fi descriptor can use an SSID or SSID prefix; provide only one. Wi-Fi Aware descriptors can identify service name, role, model, or vendor properties in the supported SDK.

Descriptor validation should check:

1. At least one required identity/filter field exists.
2. Data blobs and masks have compatible lengths.
3. The descriptor corresponds to the app’s Info.plist declarations.
4. The advertised protocol version is acceptable.
5. The match is narrow enough to avoid showing a different physical product.
6. The product image and display name are correct for the user-facing picker.

Do not treat a matching advertisement as proof of authenticity. If the product needs authenticity or pairing-mode verification, use custom filtering and a protocol handshake before enabling commands.

See [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor) and [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem).

### Picker filtering and migration

For simple discovery, provide picker display items and let the system filter matches. For advanced filtering, set ASPickerDisplaySettings to use filterDiscoveryResults, receive accessoryDiscovered events, inspect the advertised data or RSSI, create ASDiscoveredDisplayItem values, and call updatePicker(showing:).

Custom filtering may be needed to:

- verify a pairing-mode bit;
- check an accessory product/firmware version;
- authenticate a signed advertisement;
- select a specific product variant;
- fetch a local asset only when permitted by the route.

If no acceptable accessory remains, finish the picker discovery and show a useful timeout/retry state. Do not leave a blank, indefinite system picker.

For migration, use ASMigrationDisplayItem with the supported hotspot SSID or previous peripheral identifier. Apple documents that a Core Bluetooth central should not be initialized before migration completes. Record migrationComplete before starting old transport discovery.

### Accessory authorization and management

After an accessory is selected, the current ASAccessorySession surface includes access to previously selected accessories, renaming, removal, and authorization update/failure operations. Use those operations to make the user’s trust choice reversible and visible.

A “connected” row should include:

- accessory display name;
- transport and protocol version;
- last seen;
- authorization state;
- connection state;
- firmware/configuration state;
- removal/forget action;
- safe reconnect policy.

Do not use a Bluetooth identifier as the only user-facing identity. Do not automatically perform a physical side effect after setup without confirmation and readback.

## DeviceDiscoveryUI

### App-to-app and app-to-device pairing

DeviceDiscoveryUI provides system UI for connecting iOS, iPadOS, tvOS, watchOS, and Mac Catalyst apps over peer-to-peer networks. It uses a secure, encrypted pairing mechanism and can provide a selected endpoint to the app.

The main SwiftUI route is:

    publisher advertises a declared service
        -> DevicePairingView
        -> subscriber presents DevicePicker
        -> person selects and authorizes a device
        -> onSelect returns an endpoint
        -> Network/NWConnection sends the app protocol

DevicePicker should be presented as a full-screen modal view. The label is the preflight explanation, and the fallback is the honest unsupported-device route. The picker does not replace application-level authentication, version negotiation, authorization, or command confirmation.

Use [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker), [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview), [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess), and [DevicePickerSupportedAction](https://developer.apple.com/documentation/devicediscoveryui/devicepickersupportedaction).

### DeviceDiscoveryUI and local-network privacy

The framework can provide secure peer-to-peer connectivity without giving the app broad access to the entire local network. That does not make the connection automatically trusted. The app still needs:

- a declared service;
- a clear user intent;
- a selected endpoint;
- application-level protocol authentication;
- a version/feature handshake;
- connection timeout and cancellation;
- authorization for the action;
- safe handling of disconnection and stale state.

If the app sends a command to a physical device, treat the endpoint as a transport, not as a permission to unlock a door, move a robot, or change a safety-critical setting.

### tvOS and application services

The tvOS route uses NSApplicationServices to describe supported devices and services. Apple documents Apple TV-specific restrictions, including Apple TV 4K support, device/platform combinations, one connected device at a time, and universal-purchase considerations. Test the exact tvOS/iOS/watchOS matrix if the product includes a TV companion.

Use [Connecting a tvOS app to other devices over the local network](https://developer.apple.com/documentation/devicediscoveryui/connecting-a-tvos-app-to-other-devices-over-the-local-network) for the target-specific service and listener contract.

## Wi-Fi Aware

Wi-Fi Aware provides a peer-to-peer service model with publishable and subscribable services. The framework requires the Wi-Fi Aware entitlement and service declarations in Info.plist. WACapabilities reports supported features and maximum devices/services for the current host; an empty supported-feature set means the host does not support the capability.

The route is:

    WiFiAwareServices declaration
        -> WACapabilities supportedFeatures
        -> WAPublishableService or WASubscribableService
        -> DeviceDiscoveryUI pairing UI
        -> WAPublisherListener or WASubscriberBrowser
        -> Network connection
        -> application protocol

Service names must follow the documented service-name rules and should be registered uniquely. An invalid service name in Info.plist can crash the app. Keep the service string in one source-of-truth constant and test both publisher and subscriber targets.

WAPublisherListener and WASubscriberBrowser are transport setup layers. Define whether the product needs:

- one-to-one messaging;
- streaming media;
- bulk file transfer;
- control commands;
- low-latency sensor values;
- reconnection after range loss.

Choose NWParameters and an application-level framing/authentication protocol deliberately. A secure transport does not automatically make the app message schema safe.

Use [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware), [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities), [WAService](https://developer.apple.com/documentation/wifiaware/waservice), [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice), [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice), [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener), and [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser).

## Post-setup transport choices

After setup or pairing, choose a transport that matches the device:

| Transport | Use | Core proof |
| --- | --- | --- |
| Core Bluetooth | Custom BLE GATT service | Radio authorization, service/characteristic schema, notifications, reconnect, background, firmware |
| Network | IP or peer endpoint protocol | TLS/authentication, framing, reachability, timeout, reconnect, server/device identity |
| Wi-Fi Aware | High-throughput peer-to-peer | Entitlement, service declaration, pairing, capabilities, path lifecycle, protocol |
| HomeKit | Apple Home accessory | Home authorization, characteristic state, external edits, physical side effect |
| Nearby Interaction | Range/direction | Token/configuration, supported hardware, session invalidation, physical environment |

Do not keep an ASAccessorySession alive as if it were a permanent data transport. Its job is discovery/setup and accessory management. The post-setup connection has its own lifecycle.

## Privacy and trust

Accessory discovery can reveal nearby hardware, routines, home layout, workplace devices, and relationships. Minimize:

- accessory identifiers;
- Bluetooth advertisement payloads;
- Wi-Fi SSIDs;
- endpoint addresses;
- local-network names;
- room or home labels;
- device telemetry;
- command history.

Use system pickers and pairing UI where available. Ask for a physical side effect only after the person knows the target, value, and consequence. Keep firmware updates, pairing removal, and destructive commands behind explicit review.

On-device AI may classify a natural-language goal or propose a supported accessory operation, but it must not:

- select an unknown device by fuzzy name;
- infer trust from RSSI or proximity;
- bypass the picker or pairing confirmation;
- send arbitrary protocol bytes;
- unlock or control a physical system without deterministic validation and confirmation.

## Liquid Glass and accessory setup design

Let the system picker own the pairing moment. Use Liquid Glass in the app-owned parts:

- Add accessory entry point;
- compatibility and setup explanation;
- accessory detail and rename screen;
- connection status;
- protocol/firmware update review;
- command confirmation;
- failure and reconnect state.

Avoid putting glass over a system picker or making a connected state look like a guaranteed trusted state. A native status row should distinguish:

    discovered -> selected -> pairing -> authorized -> connecting -> connected -> stale/disconnected

Use readable text, clear icons, and a non-color state signal. Provide a reduced-motion/reduced-transparency fallback and test the setup flow with VoiceOver and Switch Control.

The [Accessory Design Guidelines](https://developer.apple.com/accessories/) and [Human Interface Guidelines design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) are relevant alongside the framework contracts.

## Evidence package

Capture:

1. Target and Info.plist declarations.
2. AccessorySetupKit/Wi-Fi Aware entitlements and signed artifacts.
3. Accessory picker and DeviceDiscoveryUI pairing invocation.
4. Accessory/device event sequence.
5. Pairing/authorization and failure paths.
6. Physical accessory or paired-device model, firmware, range, and radio state.
7. Post-setup transport handshake and message validation.
8. Disconnect, reconnect, invalidation, migration, and removal.
9. Large text, VoiceOver, reduced motion/transparency, and fallback UI.
10. AI proposal input/output and explicit command approval.
11. Battery, thermal, throughput, latency, and storage behavior where relevant.
12. Release/distribution evidence for new entitlements and targets.

Use the [accessory and discovery proof matrix](../60-verification/23-accessory-setup-and-device-discovery-proof-matrix.md) and the [accessory code recipes](../70-code-recipes/41-accessory-setup-and-device-discovery-recipes.md) before calling the route complete.

## Sources

- [AccessorySetupKit](https://developer.apple.com/documentation/AccessorySetupKit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessoryEventType](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryeventtype)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASDiscoveredDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/asdiscovereddisplayitem)
- [NSAccessorySetupSupports](https://developer.apple.com/documentation/bundleresources/information-property-list/nsaccessorysetupsupports)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [DevicePickerSupportedAction](https://developer.apple.com/documentation/devicediscoveryui/devicepickersupportedaction)
- [Connecting a tvOS app to other devices over the local network](https://developer.apple.com/documentation/devicediscoveryui/connecting-a-tvos-app-to-other-devices-over-the-local-network)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAService](https://developer.apple.com/documentation/wifiaware/waservice)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [Network](https://developer.apple.com/documentation/network)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Accessory Design Guidelines](https://developer.apple.com/accessories/)
- [Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
