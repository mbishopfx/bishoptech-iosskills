# Core Bluetooth: GATT, device roles, and background lifecycle

Core Bluetooth is the direct route for communicating with Bluetooth Low Energy and Bluetooth Classic devices. It is a transport and protocol framework, not a pairing-trust product, accessory catalog, identity system, or guarantee that a physical command succeeded.

Use this deep dive when an app needs to:

- scan for a known BLE service;
- connect to a peripheral and discover its services and characteristics;
- read, write, or subscribe to characteristic values;
- expose the iPhone or iPad as a local peripheral;
- transfer bounded data between two BLE-capable devices;
- restore a central/peripheral manager after the system relaunches the app;
- evaluate the iOS 26 Live Activity background route for a user-started Bluetooth task;
- use the Core Bluetooth Classic sample route, where the selected device and SDK support it.

Do not use this page as a substitute for AccessorySetupKit onboarding, HomeKit automation, Nearby Interaction ranging, Network Framework transport, or a product-specific cryptographic trust protocol.

## The two Bluetooth roles

Core Bluetooth exposes two primary roles:

| Role | Main object | Responsibility | Evidence boundary |
| --- | --- | --- | --- |
| Central | CBCentralManager | Scan for, connect to, and manage remote peripherals | A discovered peripheral is not a trusted product identity |
| Peripheral | CBPeripheralManager | Publish local services, advertise, and respond to remote centrals | Advertising is not authorization or secure pairing |

An iPhone can act as a central, a peripheral, or both. A product should choose the smallest role set that satisfies the user outcome. Dual-role behavior multiplies lifecycle, radio, background, battery, and protocol states.

The BLE data model is a GATT graph:

1. a peripheral advertises a service identifier;
2. the central discovers a peripheral;
3. the central connects;
4. the central discovers services;
5. the central discovers characteristics and descriptors;
6. the app reads, writes, or subscribes;
7. the protocol frames, validates, acknowledges, and reconciles data.

The system objects represent the transport. The app still owns protocol versioning, message framing, authorization, replay rules, side-effect confirmation, and durable domain truth.

## Central lifecycle

Create CBCentralManager with a delegate and wait for central state to become poweredOn before scanning or connecting. The manager may report poweredOff, unauthorized, unsupported, resetting, or unknown. These are user-visible states, not exceptions to hide in a generic “Bluetooth failed” banner.

Preferred lifecycle:

| State | App action |
| --- | --- |
| not initialized | Create one manager per intended role and stable restoration identity |
| poweredOn | Scan only for the service identifiers needed by the active feature |
| discovering | Keep a bounded candidate list and show why the app is scanning |
| candidate selected | Stop or narrow scanning; show the user-visible device identity and trust status |
| connecting | Disable duplicate connect actions and support cancellation |
| connected | Assign the peripheral delegate and discover the required service graph |
| services discovered | Validate the expected service and characteristic UUIDs |
| ready | Permit only typed operations supported by the negotiated protocol |
| disconnected | Preserve user intent if safe, then reconnect using explicit backoff |
| resetting/restoring | Reconcile manager/peripheral state before resuming work |
| denied/unsupported | Provide a useful non-Bluetooth mode or explain the missing capability |

The central manager’s RSSI value can help a product decide whether a transfer is plausible, but it is not a distance, identity, safety, or delivery guarantee. Avoid turning a single RSSI threshold into a universal proximity rule.

## Peripheral lifecycle

Create CBPeripheralManager with a delegate and wait for its state to become poweredOn before adding services or advertising. A local peripheral publishes CBMutableService and CBMutableCharacteristic objects. A remote central can then discover and interact with that GATT database.

Peripheral state needs separate handling for:

- service add failure;
- advertising failure or stop;
- central subscription and unsubscription;
- read and write requests;
- notification queue pressure;
- background suspension;
- state restoration;
- teardown when the feature or user session ends.

When updateValue returns false, the peripheral manager is signaling that its notification queue cannot accept more data immediately. Hold bounded data, wait for peripheralManagerIsReady(toUpdateSubscribers:), and apply backpressure. Do not drop frames silently or grow an unbounded buffer.

## GATT and protocol design

BLE characteristics are not a general-purpose database. Define a small protocol register:

| Field | Example policy |
| --- | --- |
| Service UUID | One stable primary service per feature family |
| Characteristic UUID | Separate command, response, event, and control paths where that improves validation |
| Encoding | Versioned binary or UTF-8 payload with explicit maximum size |
| Framing | Length, sequence, message type, payload, integrity field, and end marker if needed |
| Write mode | With response for important commands; without response only for bounded, loss-tolerant streams |
| Notification | Subscribe only after the user has entered the connected feature |
| Acknowledgement | App-level acknowledgement for domain side effects |
| Replay rule | Reject duplicate or expired command IDs |
| Capability negotiation | Device firmware version and supported operation set |
| Error model | Typed transport, protocol, authorization, and device errors |

The Core Bluetooth callback that a value changed proves a transport event. It does not prove that a motor moved, a lock changed, a measurement is accurate, or a cloud record was updated. The device should return a typed result that the app reconciles with its domain state.

## Permissions and target configuration

For apps linked on or after iOS 13, Apple documents NSBluetoothAlwaysUsageDescription as the Bluetooth privacy usage description. The string should explain the user-facing purpose at the moment the feature needs Bluetooth.

Use UIBackgroundModes only for an actual background requirement, with bluetooth-central or bluetooth-peripheral matched to the role. Background modes change the system’s scheduling and wake behavior; they do not make the app continuously runnable. Background execution remains bounded and system-controlled.

Core Bluetooth background processing is separate from a notification, a generic BackgroundTask, or a foreground assertion. The app must be prepared for suspension, termination, restoration, duplicate callbacks, stale peripherals, and unavailable radio state.

## State preservation and restoration

State restoration is opt-in. Provide a stable CBCentralManagerOptionRestoreIdentifierKey or CBPeripheralManagerOptionRestoreIdentifierKey when creating the manager on every launch. Reinstantiate the manager with the same identity and implement the matching willRestoreState delegate method.

Restored dictionaries can contain preserved peripherals, scan service identifiers, scan options, services, advertising data, or subscribed centrals. Treat these as system restoration inputs, not as proof that the app’s domain session is still authorized or current.

Restoration algorithm:

1. load the stable manager identifier;
2. recreate the correct manager and delegate;
3. accept the restored objects without assuming all fields are present;
4. reconcile restored peripherals/services with the app-owned device registry;
5. revalidate the protocol version and user authorization;
6. resume only idempotent work;
7. show stale/error state when the device, service, or command no longer matches.

If the system relaunches the app without enough restoration data, rebuild from the app-owned registry and require a new user-approved connection path where appropriate.

## iOS 26 Live Activity background route

Apple’s current Core Bluetooth documentation says that in iOS 26 and later, an app can continue certain Bluetooth activities in the background if it starts a Live Activity before entering the background, while an appropriate CBManager is instantiated. The documented examples include scanning without service UUIDs and scanning with duplicate filtering disabled.

Treat this as a narrow, target-specific route:

- the Live Activity must be started by the user-approved feature;
- the manager must be instantiated before backgrounding;
- the exact final SDK and device behavior must be verified;
- the Live Activity is a system-surface projection, not a Bluetooth permission grant;
- the app still needs cancellation, expiry, battery, radio, and termination handling;
- the user-visible Live Activity must not expose sensitive device data by default.

Do not generalize this documentation to indefinite background Bluetooth execution or to every iPad/macOS configuration. The Core Bluetooth root also documents that Core Bluetooth background execution modes are not supported in iPad apps running on macOS.

## Bluetooth Classic boundary

Core Bluetooth also contains an official “Using Core Bluetooth Classic” sample route for Bluetooth Classic devices. Treat Classic as a separate compatibility register:

- confirm the device family and protocol;
- verify the exact target SDK and supported platform;
- avoid assuming BLE GATT service/characteristic semantics apply;
- record pairing, discovery, connection, and data-flow behavior separately;
- require the actual physical device for proof.

The BLE central/peripheral recipes on this page do not prove Classic behavior.

## Privacy, security, and AI

Bluetooth advertisements, peripheral UUIDs, device names, service values, RSSI, and command payloads can be sensitive. Keep them out of analytics and AI prompts unless the user-facing purpose and retention policy justify the field.

Use a device selection and trust state separate from transport connection:

| Layer | Question |
| --- | --- |
| Discovery | Did a radio advertisement match a declared service? |
| Selection | Did the person choose this device for this task? |
| Transport | Is a connection currently established? |
| Protocol | Did the peer prove the expected version/capabilities? |
| Authorization | Is this operation allowed for this user/device/session? |
| Domain result | Did the device report a valid outcome? |

If an app uses on-device AI, let the model produce a typed, allowlisted command proposal or diagnostic explanation. Deterministic code must validate characteristic, payload size, range, current authorization, confirmation requirement, and idempotency before writing. Never let a generated string become an arbitrary BLE write.

## Native Liquid Glass design

Use Liquid Glass for app-owned status, device-selection, and command-review surfaces. Keep the hierarchy functional:

1. device name and connection status;
2. last verified device event;
3. pending command or sensor observation;
4. explicit Confirm, Cancel, Retry, and Remove actions;
5. advanced protocol diagnostics behind a secondary route.

Do not put every scanned device, raw RSSI value, or live telemetry stream into translucent cards. Glass should group actions and status, not hide trust or make an unverified connection look like a confirmed physical effect. Provide a plain, legible fallback for reduced transparency, Dynamic Type, VoiceOver, and unsupported material.

## Proof boundary

| Claim | Required evidence |
| --- | --- |
| Bluetooth capability is configured | Target membership, usage description, role/background configuration, compile |
| Central scanning works | Signed physical device with Bluetooth on, permission, known fixture, and discovery log |
| Peripheral connection works | Physical central/peripheral pair, connection/disconnection record, exact firmware |
| GATT graph is correct | Service/characteristic discovery record and UUID register |
| Data transfer works | Framed payload, acknowledgements, retry/backpressure, and integrity record |
| Device command succeeded | Device-reported domain result, not a write callback alone |
| Background route works | Configured background mode, physical lock/background run, wake/restoration evidence |
| State restoration works | Terminated/relaunched app with restoration identifier and reconciled state |
| iOS 26 Live Activity route works | User-started ActivityKit surface, target/device/SDK record, background Bluetooth evidence |
| AI stays bounded | Typed proposal audit, allowlist validation, redacted inputs, no external upload |
| Release is eligible | Final signed artifact, usage strings, capabilities, physical/system proof, and release review |

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [CBManager](https://developer.apple.com/documentation/corebluetooth/cbmanager)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [Transferring data between Bluetooth Low Energy devices](https://developer.apple.com/documentation/corebluetooth/transferring-data-between-bluetooth-low-energy-devices)
- [Central manager state restoration options](https://developer.apple.com/documentation/corebluetooth/central-manager-state-restoration-options)
- [Peripheral manager state restoration options](https://developer.apple.com/documentation/corebluetooth/peripheral-manager-state-restoration-options)
- [Core Bluetooth background processing for iOS apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Using Core Bluetooth Classic](https://developer.apple.com/documentation/corebluetooth/using-core-bluetooth-classic)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [CBATTRequest](https://developer.apple.com/documentation/corebluetooth/cbattrequest)
- [CBError](https://developer.apple.com/documentation/corebluetooth/cberror)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
