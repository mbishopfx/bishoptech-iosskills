# AccessorySetupKit and peer-pairing capability route

Use this route when an app must add a physical accessory, pair two app instances, connect to a TV/Watch/device, or establish a Wi-Fi Aware link. Start by choosing the system-owned setup surface; then define the post-setup transport and protocol.

## Outcome

Build a feature that can:

- explain and initiate accessory/device setup;
- use AccessorySetupKit or DeviceDiscoveryUI for system discovery and consent;
- receive the selected accessory or endpoint;
- connect with Core Bluetooth, Network, Wi-Fi Aware, HomeKit, or another chosen transport;
- authenticate and negotiate a versioned app protocol;
- expose safe commands/data;
- handle disconnect, removal, invalidation, migration, and stale state;
- keep device identifiers and raw advertisement data out of unnecessary logs and AI inputs.

This is not a generic “Bluetooth screen.” The setup, transport, trust, command, and physical-effect boundaries are separate.

## Choose the route

| Need | Use | Avoid |
| --- | --- | --- |
| Onboard a known hardware accessory | AccessorySetupKit | Broad custom scanning before user intent |
| Migrate an existing BLE/Wi-Fi setup | AccessorySetupKit migration items | Starting Core Bluetooth before migration completes |
| Pair two copies of an app | DeviceDiscoveryUI | Exposing all local-network devices yourself |
| Pair app to device with Wi-Fi Aware | DeviceDiscoveryUI + Wi-Fi Aware | Treating Wi-Fi Aware service discovery as app authentication |
| Connect to a custom BLE protocol after setup | Core Bluetooth | Assuming setup is a persistent connection |
| Connect to a network endpoint | Network | Trusting an NWEndpoint without an application handshake |
| Control Apple Home accessories | HomeKit | Using AccessorySetupKit for an existing Home model |
| Measure distance/direction | Nearby Interaction | Treating proximity as identity or trust |

## Target and resource register

| Target | Responsibility | Required register |
| --- | --- | --- |
| iOS/iPadOS app | User intent, picker, setup, detail, command review | AccessorySetupKit usage/Info.plist, transport capability, protocol |
| watchOS companion | Optional post-setup Core Bluetooth interaction | watchOS availability, pairing/companion state, physical watch proof |
| tvOS app | DeviceDiscoveryUI publisher/subscriber path | NSApplicationServices, supported platforms, universal purchase |
| Wi-Fi Aware target | Publish/subscribe services and peer transport | WiFiAwareServices, Wi-Fi Aware entitlement, service names |
| Shared protocol module | Messages, versions, capabilities, validation | Sendable/value types, no UI or raw framework objects |
| Extension/system target | Only if the chosen product route requires it | Target membership, process lifetime, signed artifact |

Before implementation, record:

- deployment targets and SDK;
- accessory families and firmware versions;
- Bluetooth service/company/name values;
- Wi-Fi SSID/prefix or Wi-Fi Aware service;
- setup and transport entitlements;
- required Info.plist declarations;
- whether temporary or permanent pairing is desired;
- app-level authentication and command policy;
- physical devices and accessories available for proof.

## Route A: AccessorySetupKit onboarding

### A1. Declare supported products

Add the current AccessorySetupKit support key and Bluetooth/Wi-Fi identifiers. Keep declarations narrow and synchronized with ASDiscoveryDescriptor values. Add product images and names as app resources.

### A2. Activate the session

Create ASAccessorySession and activate it on the queue that will serialize events. Set a single event handler and map event types into a small app-owned state machine.

### A3. Show the system picker

Create an ASPickerDisplayItem per supported product/variant. Each item contains a display name, product image, and ASDiscoveryDescriptor. Present it from an explicit Add action after the app has explained the feature.

### A4. Handle selection after dismissal

Store the accessory from accessoryAdded. Wait for pickerDidDismiss before presenting an app-owned detail/configuration screen. Handle accessoryChanged, accessoryRemoved, invalidated, pickerSetupFailed, and migrationComplete.

### A5. Connect after setup

Use the selected ASAccessory’s supported identifiers to create the actual transport. Run:

    transport connected
        -> protocol hello
        -> accessory identity/version
        -> app authorization
        -> capability read
        -> safe command surface

Do not perform a physical side effect as the first message. Read current state, show the target and consequence, then require user confirmation.

## Route B: custom filtering

Use picker filtering only when the simple descriptor is not enough:

- set picker display settings to filter discovery results;
- handle ASAccessoryEventType.accessoryDiscovered;
- validate advertisement/product/firmware/pairing mode;
- create ASDiscoveredDisplayItem;
- call updatePicker(showing:);
- finish discovery on timeout or empty acceptable results.

Filtering is a product trust boundary. Keep the code deterministic and bounded. If authenticity needs cryptography or a challenge-response, define that protocol explicitly and record failure/retry states.

## Route C: migration

For a product that already uses Core Bluetooth or Wi-Fi:

1. Build ASMigrationDisplayItem values from the supported prior identifier.
2. Present the migration picker.
3. Wait for migrationComplete.
4. Only then initialize or resume the legacy transport.
5. Reconcile the new ASAccessory list with the old app-owned device records.
6. Ask the person to resolve duplicate or ambiguous records.

Do not silently merge a migrated accessory with a different physical device because names match.

## Route D: DeviceDiscoveryUI pairing

### D1. Describe the service

For app-to-app or app-to-device pairing, define the service the publisher provides and the platforms that can connect. Use DevicePairingView on the publisher side and DevicePicker on the subscriber side where appropriate.

### D2. Check support and present full screen

Read the current support environment/feature. Present DevicePicker full screen with:

- label: clear purpose and data/control consequence;
- fallback: unsupported platform/device explanation;
- onSelect: receive endpoint and begin connection;
- parameters: default application-service settings or a reviewed Network protocol.

Cancellation should return to the app without an error banner.

### D3. Connect and authenticate

The endpoint is a transport result. Create NWConnection/NWListener or the chosen Wi-Fi Aware path, then exchange:

- protocol version;
- service intent;
- device/app identity;
- capability list;
- challenge/response or app authorization;
- sequence number and idempotency policy.

Only after the handshake should the app enable command controls.

## Route E: Wi-Fi Aware

1. Add the Wi-Fi Aware entitlement.
2. Declare WiFiAwareServices with publishable/subscribable service configuration.
3. Check WACapabilities.supportedFeatures and maximum counts.
4. Resolve WAPublishableService or WASubscribableService from allServices.
5. Present DevicePairingView or DevicePicker.
6. Use WAPublisherListener or WASubscriberBrowser to create the Network path.
7. Apply a versioned message protocol with bounded frames and cancellation.

Use a unique service name following the documented service-name rules. Treat a service string as a product API: changing it can break discovery.

## State machine

| State | Source | Next actions |
| --- | --- | --- |
| idle | App | Show Add/Pair |
| preparing | App | Validate target, plist, descriptor |
| discovering | System picker/session | Wait, cancel, handle invalidation |
| selected | Picker event | Wait dismissal, inspect accessory/endpoint |
| pairing | System | Show progress, handle failure |
| authorized | System/app | Start transport |
| connecting | Transport | Timeout, cancel, retry |
| handshaking | Protocol | Validate version, identity, capabilities |
| connected | Transport + protocol | Enable safe commands |
| stale | Last observation | Refresh/reconnect; disable risky action |
| disconnected | Transport | Retry, remove, or manual pairing |
| removed | Accessory session | Clear association and re-add |
| invalidated | Session | End old session and recover intentionally |
| failed | Any layer | Show layer-specific recovery |

Keep session state, transport state, protocol state, and physical-effect state as separate fields.

## Protocol and command contract

Every message should have:

- schema version;
- message ID;
- request/response or event type;
- sequence number;
- target identity;
- expiry or timeout;
- payload validation;
- result/error code;
- idempotency behavior.

For commands that change the physical world:

1. show target and action;
2. read current state if possible;
3. confirm the person’s intent;
4. send a bounded command;
5. wait for a matching result;
6. re-read state;
7. show success only after confirmation.

No generated text or model tool should skip this path.

## AI route

AI can help:

- turn a natural-language request into a device/service proposal;
- summarize a capability list;
- produce human-readable protocol error copy;
- suggest a reconnect step;
- label a selected accessory with user-approved metadata.

AI cannot:

- choose an ambiguous device automatically;
- infer ownership from RSSI, name, or proximity;
- bypass system pairing;
- send arbitrary bytes;
- select a dangerous physical command;
- treat a connection as approval;
- retain raw advertisements or local-network details without a reviewed reason.

Review shell:

    Request: “Send the selected video to the living-room display”
    Target: selected display, paired 2 minutes ago
    Service: file-transfer v2
    Payload: video.mov, 420 MB
    Risk: transfer can be canceled; receiver will store a copy
    Actions: Cancel, Send

The model proposes. Deterministic validation and the person commit.

## Privacy and security

Minimize and redact:

- Bluetooth identifiers and advertisements;
- Wi-Fi SSIDs;
- endpoints and IP addresses;
- device names and room labels;
- serial numbers;
- pairing/PIN data;
- protocol payloads;
- physical-command history.

Use Keychain for secrets and a versioned protocol for trust. Do not put credentials in the picker, shared logs, prompts, widgets, or crash messages.

## Build sequence

1. Choose AccessorySetupKit, DeviceDiscoveryUI, or another primary route.
2. Create the target/Info.plist/entitlement register.
3. Implement pure descriptors, policy, protocol, and state tests.
4. Add system picker and event handling.
5. Add post-setup transport and handshake.
6. Add connection/reconnect/removal.
7. Add safe command confirmation.
8. Add optional Wi-Fi Aware or companion target.
9. Add AI proposal and review.
10. Run physical device/accessory, accessibility, performance, privacy, and release evidence.

## Acceptance checklist

- [ ] Discovery, pairing, transport, protocol, and trust are separate.
- [ ] AccessorySetupKit Info.plist identifiers match descriptors.
- [ ] DeviceDiscoveryUI has a label, fallback, and cancellation path.
- [ ] Wi-Fi Aware support and service declarations are gated.
- [ ] System events are mapped to an idempotent state model.
- [ ] Migration waits for migration completion.
- [ ] Physical commands require target/readback/confirmation/result.
- [ ] Disconnection and invalidation do not leave a fake connected state.
- [ ] AI cannot bypass selection, pairing, authorization, or protocol validation.
- [ ] Sensitive accessory/network data is minimized and redacted.
- [ ] VoiceOver, Dynamic Type, reduced effects, and physical ergonomics are tested.
- [ ] Signed entitlements and accessory/peer hardware evidence are recorded.

## Sources

- [AccessorySetupKit](https://developer.apple.com/documentation/AccessorySetupKit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessoryEventType](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryeventtype)
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
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [Network](https://developer.apple.com/documentation/network)
- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [Nearby Interaction](https://developer.apple.com/documentation/nearbyinteraction)
- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Accessory Design Guidelines](https://developer.apple.com/accessories/)
