# SwiftUI Core Bluetooth and nearby-accessory review

This deep dive covers the SwiftUI-specific boundary around Core Bluetooth: central and peripheral role selection, permission and radio state, discovery and connection ownership, GATT service/characteristic projection, typed transport, background and restoration limits, safe command review, and on-device AI proposals.

It extends [Core Bluetooth GATT and background lifecycle](26-core-bluetooth-gatt-and-background-lifecycle.md), [HomeKit, Bluetooth, and Nearby Interaction](02-homekit-bluetooth-and-nearby.md), and the [Core Bluetooth transport and device-command route](../50-capability-recipes/49-core-bluetooth-transport-and-device-command-route.md). Those pages explain the lower-level transport and device contracts; this page explains how SwiftUI should expose them without treating a discovered peripheral or a connected callback as trusted product truth.

## The transport boundary

Use this sequence:

~~~text
target, usage description, and role configuration
  -> CBManager authorization and state
  -> central/peripheral lifecycle owner
  -> discovery or advertising
  -> stable identity and protocol trust
  -> GATT service/characteristic discovery
  -> typed value projection
  -> explicit user intent or AI proposal
  -> validated bytes and write policy
  -> notification/response/reconnect reconciliation
  -> physical-device and release evidence
~~~

Core Bluetooth hides much of the Bluetooth Low Energy protocol, but it does not decide what a device means, whether a UUID belongs to the intended physical product, whether a byte sequence is safe, or whether a write produced the desired physical effect.

Keep these authorities separate:

| Fact or action | Owner | SwiftUI meaning |
| --- | --- | --- |
| Bluetooth permission and manager state | System and CBManager | Allowed, denied, powered off, resetting, unsupported, or unknown. |
| Discovered peripheral | Core Bluetooth radio observation | A candidate with an identifier and advertisement context, not authenticated product identity. |
| GATT services and characteristics | Remote peripheral database | A discovered protocol surface whose UUIDs and properties still need product validation. |
| Typed domain value | App protocol adapter | A decoded value with revision, timestamp, and source peripheral. |
| User command | App-owned intent and safety policy | A requested effect that has not yet become a device result. |
| Bytes on the link | Protocol encoder and Core Bluetooth | A transport operation with write-type, length, response, and error semantics. |
| Physical result | Accessory and sensor feedback | Evidence that must be reconciled from a response, notification, read, or separate sensor path. |
| AI result | On-device model | A proposal or explanation with no transport authority. |

A SwiftUI Toggle is a presentation of desired intent. It is not proof that a peripheral is connected, that the characteristic accepted the bytes, or that the physical device changed.

## Choose central, peripheral, or both

| Product outcome | Role | Primary APIs | Boundary |
| --- | --- | --- | --- |
| iPhone reads or controls a sensor/accessory | Central | CBCentralManager, CBPeripheral, CBService, CBCharacteristic | Scan, connect, discover, read/write/notify, and reconcile. |
| iPhone advertises a service to another device | Peripheral | CBPeripheralManager, CBMutableService, CBMutableCharacteristic, CBCentral | Publish, advertise, handle requests/subscriptions, and protect data. |
| Two iOS devices exchange bounded data | Both | Central and peripheral managers | Define one protocol and independently prove each role. |
| Nearby distance/direction context | Nearby Interaction plus transport | NISession and a separate exchange transport | Do not infer identity or command authorization from proximity alone. |
| Home automation | HomeKit/Matter | HomeKit or MatterSupport | Use the system home model when the device belongs there; do not replace it with raw BLE. |

Do not add the peripheral role because it sounds more capable. It changes Info.plist, background, protocol, privacy, and physical proof requirements. A central-only product should keep the local device’s role clear.

## Authorization and manager state

For current iOS targets, include NSBluetoothAlwaysUsageDescription with a concise purpose statement that describes the concrete feature. Older deployment targets have additional historical usage-description requirements; verify the selected deployment matrix.

Read CBManager.authorization and wait for the manager state before scanning, connecting, advertising, or publishing services:

~~~text
notDetermined -> system permission -> allowedAlways
                                 -> denied
                                 -> restricted

unknown -> resetting -> poweredOn
                    -> poweredOff
                    -> unsupported
                    -> unauthorized
poweredOn -> ready for the selected role
~~~

The authorization state and hardware manager state are different:

- allowedAlways does not mean Bluetooth is powered on;
- poweredOn does not mean the user has authorized the app’s role;
- a connected CBPeripheral does not mean the application-level protocol is trusted;
- a previous permission does not guarantee the same physical device is nearby;
- a simulator or development accessory does not prove real radio behavior.

When state changes to poweredOff, resetting, unauthorized, or unsupported, stop unsafe commands and explain which part of the route is unavailable. Do not keep a “connected” card alive indefinitely.

## Manager ownership and SwiftUI lifecycle

Create one lifecycle owner per role and keep it alive for the intended session:

- CBCentralManager belongs to a central coordinator;
- CBPeripheral delegates belong to a connection/session owner;
- CBPeripheralManager belongs to a peripheral coordinator;
- SwiftUI reads value-only snapshots;
- tasks, continuations, and subscriptions are cancelled when the session ends.

Avoid:

- constructing a CBCentralManager inside a list row;
- scanning on every view appearance without an explicit session;
- replacing a peripheral delegate while a discovery operation is active;
- updating SwiftUI state from an arbitrary delegate queue;
- holding a CBPeripheral reference as a permanent identity without a product identity layer;
- assuming a restored manager can use the same in-memory objects as the previous process.

Choose a delegate queue intentionally. If the selected SDK delivers events on a private queue, serialize protocol state there and publish immutable snapshots across the UI isolation boundary. Never make a view the implicit transport state machine.

## Discovery is not identity

CBCentralManager scans for advertising peripherals. Prefer service UUID filters when the product knows the service it needs; broad scans consume more radio and create more ambiguous candidates. Stop scanning when the product has enough candidates or a connection begins.

An advertisement can contain:

- local name;
- advertised service UUIDs;
- manufacturer data;
- service data;
- signal information;
- connectability and other metadata.

Treat each field as an untrusted candidate signal:

1. show a human-readable candidate only when useful;
2. keep the peripheral identifier and advertisement revision;
3. require a protocol handshake or authenticated challenge where the product needs trust;
4. avoid using a mutable display name as identity;
5. avoid exposing raw manufacturer data in the main UI;
6. expire candidates after a product-defined freshness window.

Core Bluetooth peripheral UUIDs are system-managed identifiers. They are not necessarily a printed serial number, a cryptographic identity, or a forever-stable cross-device product ID. If the device exposes a serial or attested identity through a protected characteristic, bind that identity after a validated handshake.

## Connection and session state

Use an explicit state machine:

~~~text
idle
  -> awaitingBluetooth
  -> scanning
  -> candidateSelected
  -> connecting
  -> connected
  -> discoveringServices
  -> discoveringCharacteristics
  -> handshaking
  -> ready
ready -> reading
      -> writing
      -> subscribing
      -> reconnecting
      -> disconnected
      -> protocolFailure
      -> identityFailure
~~~

connectPeripheral requests a link; it does not prove the desired protocol or device identity. After didConnect:

1. set the peripheral delegate;
2. discover only required services;
3. discover only required characteristics;
4. verify properties and expected descriptors;
5. perform the protocol handshake;
6. derive a trusted session identity;
7. publish ready only after the adapter is ready.

On didDisconnect, preserve the last-known value with a stale marker, cancel in-flight operations safely, and apply the product’s reconnect policy. Do not reconnect forever without a user-visible session or an explicitly supported background use case.

## GATT is a typed protocol boundary

Core Bluetooth exposes CBService, CBCharacteristic, and CBDescriptor. A characteristic has properties that describe read, write, write-without-response, notify, indicate, and related capabilities. The app must define how bytes map to domain state:

| GATT item | App contract |
| --- | --- |
| CBUUID | Protocol namespace; validate against the expected accessory family. |
| CBService | Feature boundary; discover only required services. |
| CBCharacteristic | Read/write/notify endpoint; validate properties and maximum write length. |
| CBDescriptor | Formatting, user description, or protocol metadata where supported. |
| Data payload | Versioned wire message; decode with bounds and checksum/authentication rules. |
| Notification | Incremental event or state report; sequence and deduplicate as required. |

Never parse bytes directly in a SwiftUI view. Use a protocol adapter:

~~~text
CBCharacteristic callback
  -> payload length/type/version validation
  -> checksum/authentication validation
  -> decoder
  -> domain event or typed state
  -> session revision
  -> SwiftUI snapshot
~~~

Read and write semantics matter:

- a write with response gives a completion callback and can report an error;
- a write without response is best-effort and has no delivery confirmation;
- a notification is a peripheral-to-central report, not necessarily an acknowledgment of the app’s last command;
- a maximum write value length depends on the selected write type;
- a fragmented protocol needs its own framing, timeout, backpressure, and reassembly.

If the accessory’s protocol does not define acknowledgment, do not label the UI “completed” after a write-without-response. Use “sent” or “awaiting device report” and keep the physical effect separate.

## Reads, writes, and notifications

Use a command owner:

~~~text
user intent
  -> current session and identity check
  -> property and payload validation
  -> safety/confirmation policy
  -> queue or write operation
  -> response/notification/read
  -> domain state reconciliation
  -> UI result
~~~

For a numeric value:

- validate unit, range, scale, and endian/encoding;
- clamp only when product policy explicitly says so and show the resulting value;
- serialize writes if the accessory cannot process them concurrently;
- use write-with-response when delivery confirmation matters.

For a safety-sensitive command:

- identify the physical device and location;
- show the exact target effect;
- verify the session identity and protocol revision;
- require explicit confirmation;
- never apply an AI suggestion automatically;
- show failure and recovery.

Notifications should be enabled only for values the product needs. Disable them when the session ends unless the documented background/session policy requires otherwise. Reconcile after reconnect because the last notification may not represent current device state.

## Background execution and restoration

Core Bluetooth background modes are not a promise of an always-running app. By default, many Bluetooth tasks are disabled while an iOS app is backgrounded or suspended. A product can declare bluetooth-central or bluetooth-peripheral in UIBackgroundModes for supported use cases, but background scanning behavior changes, duplicate discoveries can be coalesced, and the system can still terminate the app.

State preservation and restoration is opt-in:

1. initialize the manager with restoration options;
2. reinstate the manager when relaunched;
3. implement the appropriate willRestoreState delegate;
4. reconstruct session state from restored peripherals, services, subscriptions, and app-owned durable records;
5. revalidate protocol identity before side effects.

When woken in the background:

- do only the work related to the Bluetooth event;
- keep processing bounded;
- persist a checkpoint quickly;
- do not launch a full AI scan or upload the entire device history;
- assume the process can be terminated again;
- test the release target on a physical device.

Background restoration proves a lifecycle route only when the actual Info.plist, manager initialization, termination/relaunch, and physical event are recorded. A background mode string or foreground callback is not proof.

## Peripheral-role boundary

If the app acts as a peripheral:

- CBPeripheralManager must reach poweredOn before publishing or advertising;
- CBMutableService and CBMutableCharacteristic define a local GATT database;
- read/write/subscription requests need authorization and bounded response behavior;
- sensitive data should require an authenticated or paired connection when the protocol supports it;
- advertising data has size and background behavior limits;
- the app needs a clear session policy for when to advertise;
- background publication/advertising changes under bluetooth-peripheral.

Do not assume a local CBPeripheralManager is available on every target or that an iPhone can act as the same type of accessory as a hardware device. Separate central, peripheral, and two-device proofs.

## Native SwiftUI and Liquid Glass design

Use a functional hierarchy:

~~~text
connection context: device identity, session, last update
  glass status group
service/value groups: typed state and units
  native control or read-only value
command result: sent, acknowledged, reported, failed
detail route: protocol/support/diagnostics
AI review: proposal, source snapshot, warnings, apply
~~~

Liquid Glass should contain related status or actions, not replace transport truth. Provide system-material or opaque fallback for reduced transparency, increased contrast, unsupported targets, and accessibility settings. Do not show a glowing “connected” glass badge while service discovery or protocol handshake is incomplete.

Use native controls:

- Toggle only for a reported Boolean state with an explicit command policy;
- Slider/Stepper for a bounded typed value;
- Picker for a protocol enumeration;
- Button for one-shot commands;
- confirmation dialog for physical or security consequences.

The UI should distinguish:

| State | Copy and control |
| --- | --- |
| Scanning | “Looking for nearby devices” with cancel. |
| Candidate | Device name plus “Not connected” and trust/setup action. |
| Connecting | Progress, cancel/disconnect where safe. |
| Discovering | Explain that the device is being inspected. |
| Handshake | “Verifying accessory” rather than “Ready.” |
| Ready | Current typed state, update time, and controls. |
| Stale | Last-known state and reconnect/refresh action. |
| Writing | “Sending” or “Awaiting device response.” |
| Reported | State confirmed by response/notification/read. |
| Failed | Prior state, error reason, retry/setup/support. |

## On-device AI boundary

A local model can:

- summarize selected sensor values;
- explain a known protocol state in plain language;
- draft a typed command from a natural-language request;
- suggest which supported service to inspect;
- generate a support checklist from a selected error.

It must not:

- choose a peripheral solely from a name or RSSI;
- infer identity, consent, safety, or occupancy;
- invent a GATT UUID or byte payload;
- bypass authentication or handshake;
- use write-without-response as proof of delivery;
- issue a command without explicit confirmation;
- claim physical completion without a device report;
- receive secrets, pairing keys, or raw credentials.

Bind every proposal to:

- peripheral/session identity;
- protocol revision;
- selected service/characteristic UUID;
- typed value and encoding;
- source state revision and timestamp;
- warnings and confirmation requirement.

At apply time, re-resolve the current peripheral and characteristic, validate the protocol, and reject stale or ambiguous proposals.

## Privacy, accessibility, and energy

Bluetooth may reveal nearby devices, routines, location-adjacent patterns, medical sensor information, or physical security context. Request permission in context, minimize collection, and do not send a broad discovery feed to analytics or a cloud model.

For accessibility:

- expose device identity and connection state in VoiceOver;
- include freshness and “awaiting response” in accessibility values;
- preserve focus after reconnect and async state changes;
- support Dynamic Type and long accessory names;
- test Voice Control, Switch Control, keyboard, pointer, and reduced motion;
- never use RSSI color or animation as the only state signal.

For energy:

- scan only when needed and stop promptly;
- filter by service UUID when possible;
- avoid allow-duplicates unless the product requires it;
- discover only required services/characteristics;
- subscribe to changing values instead of polling;
- disconnect when the session is complete;
- bound reconnect attempts and background work;
- measure radio and CPU behavior on representative hardware.

## Evidence boundary

A Core Bluetooth import proves nothing about a radio route. A discovered peripheral proves a candidate observation. A service-discovery callback proves a GATT surface was returned. A write-with-response proves the accessory acknowledged a transport operation, not necessarily the physical result.

Minimum evidence:

- target capability, NSBluetoothAlwaysUsageDescription, background modes, signing, and selected SDK;
- authorization allow/deny/restricted and poweredOn/poweredOff/resetting/unsupported states;
- filtered discovery, duplicate policy, candidate expiry, and identity handshake;
- connection, service, characteristic, descriptor, read/write, notification, timeout, and reconnect fixtures;
- write-with-response and write-without-response distinction;
- background wake, termination, restoration, and bounded processing where claimed;
- peripheral-role or two-device route when included;
- physical accessory with the release build and real protocol response;
- AI stale-session, ambiguous-device, invalid-payload, and safety-confirmation rejection;
- VoiceOver, Dynamic Type, alternate input, reduced effects, energy, privacy, archive, and release evidence.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [About Core Bluetooth](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/AboutCoreBluetooth/Introduction.html)
- [Core Bluetooth Overview](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothOverview/CoreBluetoothOverview.html)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [CBManagerState](https://developer.apple.com/documentation/corebluetooth/cbmanagerstate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBService](https://developer.apple.com/documentation/corebluetooth/cbservice)
- [CBCharacteristic](https://developer.apple.com/documentation/corebluetooth/cbcharacteristic)
- [CBDescriptor](https://developer.apple.com/documentation/corebluetooth/cbdescriptor)
- [CBUUID](https://developer.apple.com/documentation/corebluetooth/cbuuid)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [Core Bluetooth Background Processing for iOS Apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Best Practices for Interacting with a Remote Peripheral Device](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/BestPracticesForInteractingWithARemotePeripheralDevice/BestPracticesForInteractingWithARemotePeripheralDevice.html)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Protected resources](https://developer.apple.com/documentation/bundleresources/information_property_list/protected_resources)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
