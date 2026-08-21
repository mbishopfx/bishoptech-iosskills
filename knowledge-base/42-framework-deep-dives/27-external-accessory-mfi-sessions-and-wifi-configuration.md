# External Accessory: MFi sessions and Wi-Fi configuration

External Accessory is Apple’s route for an iOS or iPadOS app that supports an MFi accessory connected through Lightning, an older 30-pin connector, or supported Bluetooth wireless technology. It is not a generic Bluetooth scanner and does not replace Core Bluetooth, AccessorySetupKit, HomeKit, Network, or WatchConnectivity.

Use this deep dive when the accessory manufacturer provides:

- an MFi accessory identity and supported protocol specification;
- a reverse-DNS protocol string for the app target;
- a session protocol carried by input and output streams;
- optional MFi Wi-Fi accessory configuration support;
- a physical or supported wireless accessory that the target device can actually connect to.

Apple’s current documentation says iPad and iPhone apps running on a Mac with Apple silicon cannot connect to external accessories with this framework, although they can still link the framework and run other app features. Record that platform boundary before promising Mac Catalyst or iPad-on-Mac behavior.

## Manufacturer and protocol boundary

The accessory manufacturer decides which third-party apps may communicate with the hardware. The app needs the manufacturer’s protocol documentation, supported protocol strings, framing rules, firmware compatibility, and physical test access.

The target declares supported protocols in UISupportedExternalAccessoryProtocols. Protocol names use reverse-DNS strings. At runtime, EAAccessory.protocolStrings reports the protocols the accessory supports at that moment. Apple explicitly advises checking this list before creating a session; an accessory can be connected but not yet authenticated, in which case the list can be empty.

This creates a hard gate:

connected -> protocol advertised -> app supports protocol -> session created -> streams configured -> framed message exchanged

Connection alone is not protocol readiness. A recognized model name, serial number, or cached accessory record is not permission to open an unsupported session.

## Framework object graph

| Object | Responsibility | Product state it does not prove |
| --- | --- | --- |
| EAAccessoryManager | Connected-accessory inventory and connect/disconnect notification delivery | That every cached object is current |
| EAAccessory | Manufacturer/device attributes, connection state, protocol list | That the protocol is authenticated or supported by the app |
| EASession | Communication channel for one accessory/protocol combination | That bytes are correctly framed or acted upon |
| InputStream | Read bytes and stream events from the accessory | That a complete message has arrived |
| OutputStream | Write bytes and stream events to the accessory | That the accessory accepted or executed a command |
| EAWiFiUnconfiguredAccessoryBrowser | Search and configure supported unconfigured MFi Wi-Fi accessories | That Wi-Fi setup is complete |
| EAWiFiUnconfiguredAccessory | Unconfigured accessory identity and configuration properties | That an app session is ready |

The manufacturer protocol remains app-owned. EASession does not format the data before or after transferring it.

## Connected accessory lifecycle

Register for local accessory notifications when the feature needs connection/disconnection changes. The system does not deliver EAAccessoryDidConnectNotification and EAAccessoryDidDisconnectNotification automatically until the app asks to receive them.

Suggested lifecycle:

| State | App action |
| --- | --- |
| inventory unavailable | Show no-accessory state and supported setup path |
| connected but protocol unknown | Inspect protocolStrings and wait for authentication |
| connected and compatible | Ask the person to choose or confirm the accessory |
| session creating | Create one EASession for the accessory/protocol pair |
| streams configuring | Assign delegates, schedule streams, and open them |
| ready | Permit typed, framed operations |
| input available | Drain bounded reads and decode complete frames |
| output writable | Send bounded bytes through the protocol writer |
| interrupted/disconnected | Close streams, mark stale, and reconcile |
| accessory removed | Clear or preserve app-owned record according to product policy |

EAAccessoryManager.connectedAccessories is dynamic. Apple’s docs say not to cache the array itself; re-read it when the app receives a relevant notification or re-enters the feature.

## Session and stream lifecycle

After creating an EASession, immediately retrieve and configure its streams. Assign a StreamDelegate to receive stream events and schedule each stream on a run loop so asynchronous input/output events can arrive.

The app must handle:

- stream open, opening, closed, and error states;
- hasBytesAvailable and partial reads;
- hasSpaceAvailable and partial writes;
- end-of-message framing;
- output backpressure;
- malformed or oversized frames;
- accessory disconnect during a write;
- app backgrounding and teardown;
- duplicate, stale, or replayed commands.

A stream read is transport input. A stream write is transport output. The domain layer should wait for a protocol acknowledgement or a device-reported result before declaring a physical operation complete.

## Protocol framing

Use a small, versioned framing layer:

| Field | Purpose |
| --- | --- |
| Version | Reject incompatible firmware/app versions |
| Message type | Separate command, response, event, error, and handshake |
| Request ID | Match response to command and suppress duplicates |
| Payload length | Bound allocation and detect partial frames |
| Payload | Typed operation data |
| Integrity | Checksum, MAC, or manufacturer-defined integrity rule |
| Result code | Distinguish accepted, rejected, busy, unsupported, and failed |
| Sequence | Detect missing, repeated, or reordered data where needed |

Do not parse JSON or binary data directly in a SwiftUI view. Keep protocol codecs testable with synthetic byte fixtures and real manufacturer examples.

## Wi-Fi accessory configuration route

External Accessory also exposes EAWiFiUnconfiguredAccessoryBrowser for supported MFi Wi-Fi accessories that are not configured. This is not the same as connecting to an already configured EAAccessory.

Configuration flow:

1. Add the Wireless Accessory Configuration capability and verify the signed entitlement.
2. Create a browser with its delegate and queue.
3. Start searching only while the user is actively looking for a supported accessory.
4. Filter the search predicate to the product family where appropriate.
5. Stop searching as soon as the desired accessory is located.
6. Ask the person to choose the accessory.
7. Call configureAccessory with the system-provided configuration UI host.
8. Handle success, user cancellation, and failure.
9. Re-read connected accessories and protocolStrings after configuration.
10. Open the app session only after the protocol gate passes.

Apple’s docs call the search power and resource intensive and instruct apps to stop immediately once the desired accessories are located. Do not run a hidden continuous setup scan.

The Wireless Accessory Configuration entitlement is com.apple.external-accessory.wireless-configuration. It permits configuring MFi Wi-Fi accessories; it is not a general Wi-Fi entitlement and does not prove network reachability or accessory protocol readiness.

## Background and platform limits

The external-accessory value of UIBackgroundModes is a target configuration for apps that need this framework’s background accessory behavior. It does not make an app permanently runnable or guarantee that a stream stays open under every device/system state.

Record separately:

- foreground session;
- background mode and user-started feature;
- stream event delivery;
- device lock/protected data state;
- accessory disconnection;
- process termination/relaunch;
- iPad/iPhone running directly versus on a Mac with Apple silicon;
- final MFi/app configuration and release approval.

Do not infer Mac-on-Apple-silicon accessory behavior from a successful framework import or a preview.

## Privacy, security, and AI

Accessory metadata can contain names, serial numbers, firmware revisions, protocol identifiers, and physical-room context. Keep identifiers and raw stream bytes out of analytics and model prompts unless the product explicitly needs them.

If AI is used:

- let it propose a typed operation or explain a device-reported state;
- keep protocol strings, stream framing, and command ranges deterministic;
- require user confirmation for physical side effects;
- validate device/session/request identity before writing;
- retain only a redacted audit record;
- use manual controls when the model is unavailable or uncertain.

Never treat generated text, a stream write, or an EASession as proof that a hardware operation occurred.

## Liquid Glass and native design

Keep system-provided Wi-Fi configuration UI system-owned. Use app-owned Liquid Glass for:

- selected accessory summary;
- protocol compatibility status;
- session state;
- command review;
- stream freshness and error recovery.

Do not make a “connected” glass card imply that a physical device is safe, authenticated, or executing a command. Show compatible, ready, stale, rejected, and unknown as distinct states. Provide a high-contrast and reduced-transparency fallback.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| External Accessory is the right route | Manufacturer protocol/transport record and target platform decision |
| App is configured for a protocol | UISupportedExternalAccessoryProtocols in signed artifact |
| Accessory is connected | Physical accessory and EAAccessoryManager observation |
| Protocol is supported now | Runtime protocolStrings contains the intended reverse-DNS string |
| Session is open | EASession created for the selected accessory/protocol |
| Streams work | Physical read/write events, partial-frame tests, backpressure, teardown |
| Command succeeded | Protocol/device-level acknowledgement or result |
| Wi-Fi configuration works | Entitlement, physical accessory, system configuration UI, status result |
| Background behavior works | Signed target, configured UIBackgroundModes, physical lock/background run |
| Mac-on-Apple-silicon support | Explicitly recorded as unsupported for accessory connection |
| AI remains bounded | Typed proposal, deterministic validation, redacted inputs, no arbitrary stream writes |
| Release is eligible | Final artifact, MFi/manufacturer approval, physical proof, distribution configuration |

## Sources

- [External Accessory](https://developer.apple.com/documentation/externalaccessory)
- [EAAccessoryManager](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager)
- [EAAccessory](https://developer.apple.com/documentation/externalaccessory/eaaccessory)
- [EASession](https://developer.apple.com/documentation/externalaccessory/easession)
- [EAAccessory protocol strings](https://developer.apple.com/documentation/externalaccessory/eaaccessory/protocolstrings)
- [EASession initialization](https://developer.apple.com/documentation/externalaccessory/easession/init%28accessory%3Aforprotocol%3A%29)
- [EASession input stream](https://developer.apple.com/documentation/externalaccessory/easession/inputstream)
- [EASession output stream](https://developer.apple.com/documentation/externalaccessory/easession/outputstream)
- [Connected accessories](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/connectedaccessories)
- [Register for local accessory notifications](https://developer.apple.com/documentation/externalaccessory/eaaccessorymanager/registerforlocalnotifications%28%29)
- [Supported external accessory protocols](https://developer.apple.com/documentation/bundleresources/information-property-list/uisupportedexternalaccessoryprotocols)
- [Wireless Accessory Configuration Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.external-accessory.wireless-configuration)
- [EAWiFiUnconfiguredAccessoryBrowser](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser)
- [Start searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/startsearchingforunconfiguredaccessories%28matching%3A%29)
- [Stop searching for unconfigured accessories](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/stopsearchingforunconfiguredaccessories%28%29)
- [Configure an unconfigured accessory](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/configureaccessory%28_%3Awithconfigurationuion%3A%29)
- [Configuration status](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessoryconfigurationstatus)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
