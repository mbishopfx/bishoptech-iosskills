# External Accessory MFi session route

Use this route for an MFi accessory whose manufacturer supplies a supported reverse-DNS protocol and physical test hardware. Keep accessory inventory, protocol readiness, EASession streams, framed messages, physical results, and Wi-Fi configuration as distinct boundaries.

This is a compile-oriented route sketch. It does not prove MFi enrollment, manufacturer approval, accessory compatibility, stream behavior, Wi-Fi configuration, background execution, or release eligibility.

## Route selector

| User goal | Route | Boundary |
| --- | --- | --- |
| Communicate with an MFi accessory already connected | External Accessory and EASession | Manufacturer protocol and stream contract |
| Configure an unconfigured MFi Wi-Fi accessory | EAWiFiUnconfiguredAccessoryBrowser | Wireless Accessory Configuration entitlement and system UI |
| Connect to an arbitrary BLE GATT device | Core Bluetooth | Different transport and protocol model |
| Add a supported wireless accessory | AccessorySetupKit | System discovery and consent |
| Control a Home accessory | HomeKit | Home authorization and accessory model |
| Talk to a local IP accessory | Network/URLSession | Network identity and application protocol |
| Transfer to Apple Watch | WatchConnectivity | Paired companion semantics |

Do not fall back from External Accessory to Core Bluetooth without confirming that the accessory exposes an independent BLE protocol that the product is authorized to use.

## Target register

Record:

| Field | Required decision |
| --- | --- |
| Accessory | Manufacturer, model, hardware revision, firmware range |
| Transport | Lightning, 30-pin legacy, Bluetooth MFi, or MFi Wi-Fi configuration |
| Protocol | Reverse-DNS string, version, framing, authentication, max frame |
| Info.plist | UISupportedExternalAccessoryProtocols |
| Entitlement | Wireless Accessory Configuration only when configuring MFi Wi-Fi accessories |
| Background | external-accessory only when the feature needs it |
| Platform | iPhone/iPad direct hardware; Mac with Apple silicon connection limitation |
| Session | One EASession per accessory/protocol pair |
| Streams | Input/output delegates, run loop, queue/backpressure |
| UI | Setup, connected, protocol-ready, stale, result-confirmed |
| AI | Typed operations, validation, confirmation, no raw stream prompt |
| Proof | Physical accessory, firmware, stream, configuration, artifact |

The manufacturer protocol and physical test fixture are first-class dependencies, not optional implementation details.

## Ownership graph

The route is:

SwiftUI -> accessory state reducer -> EAAccessoryManager/EASession adapter -> StreamDelegate -> protocol codec -> typed result -> durable app state

The app owns:

- the selected app-owned accessory record;
- the compatible protocol choice;
- session lifecycle;
- stream scheduling/teardown;
- frame buffering and limits;
- command authorization and confirmation;
- protocol result mapping;
- retention/deletion.

The system owns:

- connected-accessory notifications;
- physical/system configuration surfaces;
- transport availability;
- accessory connection lifecycle.

The manufacturer owns:

- protocol semantics;
- firmware compatibility;
- device-side authentication;
- physical side effects and result reporting.

## Connected accessory route

1. Register for local accessory notifications if the feature needs them.
2. Read the current connectedAccessories inventory at the feature boundary.
3. Present only accessories with relevant manufacturer/protocol context.
4. Ask the person to choose an accessory when multiple candidates exist.
5. Check protocolStrings for an app-supported protocol.
6. Create EASession(accessory:forProtocol:).
7. Retrieve inputStream and outputStream immediately.
8. Assign stream delegates and schedule both streams on a run loop.
9. Open the streams and wait for stream status.
10. Send a protocol handshake if required.
11. Enable typed commands only after the handshake and authorization pass.
12. Close streams and clear session state on disconnect or teardown.

Never cache connectedAccessories as permanent truth. Refresh it after connection and disconnection notifications.

## Wi-Fi configuration route

1. Add the Wireless Accessory Configuration capability.
2. Verify com.apple.external-accessory.wireless-configuration in the signed artifact.
3. Create EAWiFiUnconfiguredAccessoryBrowser with a delegate and queue.
4. Start search only from an explicit setup action.
5. Filter by product family where the manufacturer contract supports it.
6. Stop as soon as the desired accessory is found.
7. Ask the person to select the accessory.
8. Present the system configuration UI through configureAccessory.
9. Handle success, cancellation, and failure.
10. Re-read connected accessories and protocol strings.
11. Begin EASession only if the selected accessory now supports the intended protocol.

Do not show “configured” merely because the system UI dismissed. Record the status callback and revalidate the next stage.

## Stream adapter

Keep stream mechanics away from views:

~~~swift
struct AccessoryFrame: Sendable, Equatable {
    let version: Int
    let type: UInt8
    let requestID: UUID
    let payload: Data
}

protocol AccessoryCodec: Sendable {
    func decode(_ data: Data) throws -> [AccessoryFrame]
    func encode(_ frame: AccessoryFrame) throws -> Data
}

struct AccessorySessionState: Sendable, Equatable {
    var inputOpen = false
    var outputOpen = false
    var inputBuffer = Data()
    var pendingOutput = [Data]()
    var lastResult: String?
}
~~~

The codec must bound input, preserve partial frames, reject invalid lengths, and make duplicate/replay behavior explicit.

## Command route

Use:

intent -> selected accessory -> supported protocol -> session ready -> typed proposal -> confirmation -> framed output -> device acknowledgement -> domain result

The command validator checks:

- app-owned accessory identity;
- current EASession and protocol string;
- firmware/protocol version;
- operation allowlist;
- payload size and range;
- request ID and replay policy;
- authorization/confirmation;
- timeout/cancellation;
- device acknowledgement/result.

If the device result is unavailable, store unknown rather than succeeded.

## AI route

Allow the model to propose:

~~~swift
struct AccessoryCommandProposal: Sendable, Equatable {
    let accessoryID: UUID
    let operation: Operation
    let explanation: String
    let requiresConfirmation: Bool

    enum Operation: Sendable, Equatable {
        case setMode(String)
        case setLevel(Int)
        case requestStatus
        case stop
    }
}
~~~

The deterministic layer maps a proposal to the manufacturer protocol. The model cannot invent a protocol string, byte layout, accessory ID, or success claim.

## Failure matrix

| Failure | Fallback |
| --- | --- |
| No accessory | Show supported setup and manual mode |
| Accessory not authenticated | Explain that protocol readiness is pending |
| Protocol missing | Mark incompatible; do not create the session |
| Session nil | Show retry and compatibility diagnostics |
| Input stream error | Close, mark stale, and offer reconnect |
| Output has no space | Queue a bounded frame or pause |
| Malformed frame | Reject, record code, and resynchronize |
| Disconnected | Clear live status and reconcile inventory |
| Wi-Fi search unavailable | Stop and explain configuration state |
| Wi-Fi setup canceled | Return to setup without claiming success |
| AI unavailable | Keep deterministic commands |
| Device result unknown | Show unknown and offer refresh/retry |

## Evidence route

Capture:

- manufacturer protocol specification and test accessory;
- signed Info.plist protocol declaration and entitlement;
- physical connected-accessory inventory and notification records;
- supported protocol list before/after authentication;
- EASession creation, input/output stream setup, partial frames, backpressure, and teardown;
- Wi-Fi browser search, stop, system configuration UI, status result, and post-config protocol check;
- foreground/background/lock/disconnect/termination behavior;
- iPhone/iPad direct hardware versus Mac-on-Apple-silicon boundary;
- AI proposal validation, confirmation, redaction, fallback, and no-arbitrary-stream-write test;
- accessibility and Liquid Glass fallback matrix;
- final signed artifact and manufacturer/release configuration.

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
- [Configure an unconfigured accessory](https://developer.apple.com/documentation/externalaccessory/eawifiunconfiguredaccessorybrowser/configureaccessory%28_%3Awithconfigurationuion%3A%29)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
