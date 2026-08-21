# DeviceDiscoveryUI and Wi-Fi Aware peer pairing

DeviceDiscoveryUI and Wi-Fi Aware form a system-managed route for pairing nearby Apple apps, accessories, and third-party devices, then moving data over an authenticated peer-to-peer Wi-Fi connection. The route is intentionally split:

1. DeviceDiscoveryUI or AccessorySetupKit owns the user-mediated pairing and access decision.
2. Wi-Fi Aware describes publishable and subscribable services, paired-device selection, and capability limits.
3. NetworkListener, NetworkBrowser, NetworkConnection, or the Network framework carries the application protocol.
4. The app still owns message authorization, domain state, validation, idempotence, and user-visible completion.

Do not call this “just local networking.” Pairing, access scope, transport readiness, and a completed domain operation are different facts.

## Choose the narrowest pairing route

| Outcome | Primary route | What it owns | What remains app-owned |
| --- | --- | --- | --- |
| Pair two copies of an app or connect an app to a peer device | DeviceDiscoveryUI with Wi-Fi Aware or an application service | System picker, pairing dialog, encrypted peer connection setup, selected endpoint | App identity, protocol, authorization, persistence, retries, and domain effects |
| Onboard and configure a personal hardware accessory | AccessorySetupKit | Privacy-preserving accessory discovery and setup flow | Accessory protocol, configuration, firmware behavior, ownership, and device health |
| Connect to a previously paired Wi-Fi Aware device | Wi-Fi Aware plus NetworkBrowser/NetworkListener/NetworkConnection | Paired-device selection, service discovery, Wi-Fi-layer authenticated transport | Session state, application authentication, framing, backpressure, and recovery |
| Discover an ordinary local-network service | Network framework or Bonjour | Local-network browse/listen and transport primitives | Local-network permission, trust, encryption, protocol, and user authorization |
| Measure relative direction or distance | Nearby Interaction | UWB/Bluetooth-supported spatial session and measurements | Peer identity exchange, transport, action authorization, and spatial UX |
| Support a third-party media receiver in the system route picker | DeviceDiscoveryExtension and AVRoutePickerView | System media-device discovery extension and route-picker presentation | Media session, playback, receiver protocol, and route failure |

DeviceDiscoveryUI explicitly points accessory setup to AccessorySetupKit. Keep the two product stories separate: a file-transfer app may pair another app, while an accessory companion app may need setup, ownership, and configuration.

## DeviceDiscoveryUI pairing surfaces

### Publisher: DevicePairingView

Use SwiftUI DevicePairingView when the current app should become discoverable and advertise a service after an explicit user action. The label is an entry point into system-managed pairing UI; it is not a custom scan button that should silently start radio discovery.

The route should have:

- a clear label such as “Make this device available” or “Add this device”;
- a short explanation of what will be shared after pairing;
- a fallback view for unsupported devices, unavailable providers, or an unavailable service;
- an access scope chosen deliberately with DDDevicePairingAccess.default or DDDevicePairingAccess.permanent;
- a post-pairing state that explains whether the device is merely paired, currently reachable, or actively connected.

DevicePairingView is a SwiftUI control. UIKit targets can use DDDevicePairingViewController with a ListenerProvider and the same access decision. Do not build a fake glass discovery list around the system picker: the system owns the trust moment.

### Subscriber: DevicePicker

Use SwiftUI DevicePicker when a person chooses a nearby device or another copy of the app. Apple’s documentation says to present the picker as a full-screen, modal view. If the person cancels, the picker closes without treating cancellation as an error. If the current device does not support discovery, the fallback view is shown.

DevicePicker can be constructed from:

- an application-service NWBrowser.Descriptor;
- a Wi-Fi Aware browser provider;
- an access scope;
- an onSelect closure that receives the selected endpoint;
- a label and a fallback view;
- optional NWParameters or a protocol-framer configuration.

The selected endpoint is not the completed connection. Treat the onSelect callback as “the user selected a candidate endpoint.” Create the NetworkConnection, observe its state, and only enable domain actions after the connection reaches the application’s ready state.

UIKit targets can use DDDevicePickerViewController. The controller exposes a selected endpoint after the person chooses a device and provides a support check for the requested browser descriptor and parameters.

### Access scope

DeviceDiscoveryUI documents a default access level and a permanent access level. The default asks the system to use its default access behavior for the user-selected device. Permanent access grants the app continuing access to the selected device for future use.

Use the least persistent choice that satisfies the feature:

| Access decision | Use when | Product consequence |
| --- | --- | --- |
| default | The person is making a one-off connection or the system’s normal access behavior is enough | The app must be prepared for access to disappear and should explain that a future pairing may be needed |
| permanent | The person is intentionally adding a trusted peer for repeated use | The app must expose removal/revocation, avoid silently retaining stale peers, and protect future background or reconnect behavior |

Permanent access is not an app-level authorization model. It does not authorize every command, file, record, or remote side effect. Store only the minimum local association required to render the peer and reconstruct the transport.

## Wi-Fi Aware configuration contract

Wi-Fi Aware has a target configuration contract before code can safely use the framework.

1. Add the Wi-Fi Aware capability to the owning target.
2. Configure the com.apple.developer.wifi-aware entitlement with Publish, Subscribe, or both.
3. Declare every service under the WiFiAwareServices Information Property List key.
4. Use a valid, unique service name with the required protocol suffix.
5. Read WACapabilities before exposing a feature.
6. Pair devices through DeviceDiscoveryUI or AccessorySetupKit.
7. Select only the paired devices the product intends to reach.
8. Create a NetworkListener, NetworkBrowser, or NetworkConnection with a deliberate protocol and performance mode.

Apple documents the entitlement as an array of strings. Publish permits publishing a service and accepting incoming connections. Subscribe permits subscribing to a service and making outgoing connections. A target that only subscribes should not request Publish merely because a sample project included both.

### Service declarations

The WiFiAwareServices key is a dictionary whose keys are fully qualified service names. Each service must declare Publishable, Subscribable, or both. The service-name rules are strict: use a valid name component, the underscore and protocol suffix, and the same exact string in the target’s property list.

Example shape:

~~~xml
<key>WiFiAwareServices</key>
<dict>
    <key>_example-service._tcp</key>
    <dict>
        <key>Publishable</key>
        <dict/>
        <key>Subscribable</key>
        <dict/>
    </dict>
</dict>
~~~

The framework creates WAPublishableService values for entries with Publishable and WASubscribableService values for entries with Subscribable. Invalid service names or a service dictionary with neither role is a configuration defect that can crash the app. Treat the property list as code, inspect the signed artifact, and do not rely on a runtime fallback for malformed declarations.

### Capability and hardware checks

WACapabilities exposes supportedFeatures and maximum counts for connectable devices, publishable services, and subscribable services. Use it to decide whether to show the feature, show an explanation, or offer another route.

Apple’s current Wi-Fi Aware overview lists support for iPhone 12 and later, iPad 10th generation and later, iPad Air 4th generation and later, iPad Pro 11-inch 3rd generation and later, iPad Pro 12.9-inch 5th generation and later, and iPad mini 6th generation and later. Treat that list as a starting availability register, not as proof that every target SDK, region, accessory, OS build, or future device behaves identically.

When the feature matters, record:

- target deployment and SDK;
- device model and OS build;
- WACapabilities.supportedFeatures;
- maximum service/device limits;
- entitlement values in the signed app;
- service declarations in the signed Info.plist;
- the pairing provider and access level;
- the transport protocol and performance mode.

## Pairing and transport are separate lifecycles

The app should model a state machine rather than a Boolean isConnected flag:

| State | Meaning | Allowed UI |
| --- | --- | --- |
| unsupported | The host or provider cannot present the requested discovery route | Explain the limitation and offer a supported route |
| configured | The target has the capability and service declaration | Offer pairing |
| pairing | System-owned UI is asking the person to select or authorize a peer | Do not claim the peer is connected |
| paired | The system has an accessible WAPairedDevice or remembered application-service relationship | Offer connect or forget |
| browsing | NetworkBrowser or NWBrowser is searching for the declared service | Show searching with cancellation |
| candidate | A peer endpoint is available | Validate identity and intent before connecting |
| connecting | NetworkConnection or NWConnection is negotiating transport/security | Disable duplicate sends; allow cancel/retry |
| ready | The transport and application protocol are ready | Enable only authorized actions |
| degraded | The peer or path is temporarily unavailable | Preserve local state and offer retry |
| closing | The connection is being torn down | Drain or cancel pending work |
| revoked | The person removed access or the paired-device set changed | Remove secrets/associations as required and require re-pairing |

WAPairedDevice.allDevices is an asynchronous sequence of snapshots. An empty snapshot can mean that no paired devices are known or that the person removed all accessible devices. Keep a local display projection, but do not treat a cached row as proof that the peer is currently reachable.

## Network framework route

The newer Wi-Fi Aware route integrates with Network framework types:

- NetworkListener publishes a service and accepts incoming connections;
- NetworkBrowser subscribes to a service and returns browse-result endpoints;
- NetworkConnection creates the secure data connection;
- NWParameters configures protocol behavior;
- NWPath exposes current path information and Wi-Fi Aware performance data;
- NWError can expose Wi-Fi Aware-specific failure information.

For a publisher, select a WAPublishableService and an allowed paired-device set, create a NetworkListener, handle state updates, and retain the listener for the intended lifetime. For a subscriber, select a WASubscribableService and paired-device set, run a NetworkBrowser, review discovered endpoints, and stop browsing once the product has a suitable candidate.

Do not automatically choose the first endpoint unless the product explicitly defines that behavior. Review stable app-level identity, user choice, pairing scope, capability, protocol version, and current session state before connecting.

### Performance modes and protocols

Apple’s Wi-Fi Aware examples distinguish bulk and realtime performance modes. Bulk is the recommended choice for most transfers. Realtime is for latency-sensitive flows and needs a measured reason. The publisher and subscriber must agree on the performance mode; a mismatch is not a recoverable product policy.

Choose an application transport based on semantics:

| Data | Candidate | Required policy |
| --- | --- | --- |
| File chunks or commands that must arrive in order | TCP or QUIC stream | Framing, size limits, acknowledgements, retry, and idempotence |
| Time-sensitive state where old samples can be discarded | UDP or a datagram flow | Sequence numbers, freshness windows, loss tolerance, and explicit stale-state handling |
| Typed event protocol | Network framework protocol stack or NWProtocolFramer | Versioning, decode limits, authentication, and cancellation |
| Media or sensor stream | Realtime mode only when measured; otherwise bulk | Backpressure, dropped-frame policy, interruption, and resource budget |

Wi-Fi-layer encryption and pairing are valuable protections, but they do not define the app’s command authorization. Use a typed, versioned message envelope and reject unknown versions, oversized payloads, stale sequence numbers, and commands that the current local user has not approved.

## Background and resource boundaries

Apple documents that an app may connect to paired Wi-Fi Aware devices while it is running in the foreground or background. That does not mean the app is an always-running daemon. Runtime still depends on an existing platform mechanism, scheduling, process lifetime, power state, device availability, and the selected workload.

Design the background path as resumable:

1. Persist the minimum pending operation and idempotency key.
2. Recreate the transport when the app receives runtime.
3. Revalidate paired-device access and service availability.
4. Send bounded work with a deadline.
5. Record accepted, acknowledged, failed, and expired separately.
6. Close the connection and release resources.

Do not keep a high-rate realtime connection open merely to make a widget or Live Activity look fresh. A system projection is not a permission to keep the radio active.

## Trust, privacy, and application authorization

Pairing proves that the system allowed a relationship between a person-selected device and an app or service. It does not prove that the remote process is the correct business account, that a command is safe, or that a payload may be stored.

Define these boundaries explicitly:

- device identity: stable local association or app-level key, not only display name;
- pairing identity: the system-managed relationship and access scope;
- session identity: a fresh connection identifier and protocol version;
- operation identity: an idempotency key for each domain mutation;
- authorization: the local user’s approved action and any remote/domain policy;
- data policy: what may cross the peer link, how long it is retained, and how deletion propagates;
- failure policy: what happens when the peer disappears after accepting but before completing work.

Avoid logging raw endpoints, pairing metadata, personal content, or secret material. Redact device names when they can reveal a person, place, or household. Keep a peer list user-manageable and make “forget device” a real revocation path.

## AI and on-device intelligence boundary

An on-device model can help rank a user’s own paired devices, summarize transfer state, or draft a command for review. It must not invent a peer, infer authorization from a device name, or directly execute a high-impact remote command.

Use this pipeline:

~~~text
known paired-device projection
-> deterministic capability and reachability facts
-> optional model summary or command proposal
-> visible peer/action confirmation
-> validate device ID, service, protocol, schema, permissions, and idempotency
-> send typed command
-> wait for domain acknowledgement
-> render accepted, completed, failed, or expired
~~~

Keep model context narrow. Provide stable IDs and current states rather than raw discovery logs. If a model proposes “send this file to the living-room iPad,” resolve that phrase against the current WAPairedDevice projection and require confirmation before sending. The model output is a proposal; the selected endpoint, permission, transport acknowledgement, and domain result remain deterministic evidence.

## Native Liquid Glass and system-surface review

DeviceDiscoveryUI is a system-owned trust surface. Use a normal semantic control to launch it and let the system render the picker or pairing dialog. In the app-owned shell:

- show the current pairing and connection state in a compact semantic status row;
- group related status and action controls rather than applying glass to every row;
- keep the selected peer’s name, identity explanation, and access scope legible at Dynamic Type sizes;
- use a visible fallback for unsupported hardware or unavailable service declarations;
- distinguish paired, reachable, connected, and acknowledged;
- use a progress or status treatment that does not imply completion before a remote acknowledgement;
- respect Reduce Motion, Reduce Transparency, VoiceOver, Voice Control, and Switch Control;
- keep the destructive “Forget device” action separate from the primary connect action.

The system picker is not a place to add custom branding or mimic an Apple product. The app’s design responsibility is the surrounding explanation, state, error recovery, and reviewable action.

## Target and evidence register

| Contract | Source-level evidence | Runtime evidence |
| --- | --- | --- |
| DeviceDiscoveryUI route | Framework import, provider type, SwiftUI/UIKit picker, fallback | System pairing UI on a supported physical device |
| Wi-Fi Aware permission | Capability and signed entitlement with Publish/Subscribe values | Target can access the declared service |
| Service declaration | Info.plist WiFiAwareServices and valid service names | WAPublishableService/WASubscribableService appears without configuration failure |
| Host support | WACapabilities snapshot and device/OS row | Feature appears or falls back as designed |
| Pairing state | DevicePairingView/DevicePicker lifecycle | Two devices complete pairing and access removal |
| Transport | Listener/browser/connection route and typed protocol | Message round trip, disconnect, retry, and stale-peer behavior |
| Performance | Bulk/realtime reason and payload budget | Measured latency, loss, battery, and thermal observations |
| Security | Device allowlist, protocol validation, idempotency, redacted logging | Unauthorized peer/command rejected; replay or malformed message handled |
| AI boundary | Proposal schema and deterministic resolver | User sees and confirms proposal; only validated action executes |
| Release | Target membership, signing, capability approval, metadata | Distribution-signed two-device run in the intended environment |

## Sources

- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [Device picker initializer](https://developer.apple.com/documentation/devicediscoveryui/devicepicker/init%28_%3Aaccess%3Aonselect%3Alabel%3Afallback%3Aparameters%3A%29)
- [DDDevicePairingViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingviewcontroller?changes=latest_major%2Clatest_major)
- [DDDevicePickerViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepickerviewcontroller)
- [Default device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/default?changes=_6)
- [Permanent device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/permanent?changes=_7)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware?changes=_7)
- [Adopting Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware/Adopting-Wi-Fi-Aware)
- [Connecting devices for peer-to-peer Wi-Fi](https://developer.apple.com/documentation/wifiaware/connecting-paired-devices)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps?changes=_4_5&language=objc)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAService](https://developer.apple.com/documentation/wifiaware/waservice)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [WAPairedDevice](https://developer.apple.com/documentation/wifiaware/wapaireddevice)
- [WAPairedDevice.allDevices](https://developer.apple.com/documentation/wifiaware/wapaireddevice/alldevices)
- [NetworkBrowser](https://developer.apple.com/documentation/Network/NetworkBrowser)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection?changes=__2)
- [NetworkConnection Wi-Fi Aware information](https://developer.apple.com/documentation/network/networkconnection/wifiaware?changes=_1_7)
- [NWParameters Wi-Fi Aware configuration](https://developer.apple.com/documentation/network/nwparameters/wifiaware?language=objc)
- [NWEndpoint Wi-Fi Aware endpoint](https://developer.apple.com/documentation/network/nwendpoint/wifiaware?changes=__9)
- [Wi-Fi Aware entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.wifi-aware?changes=__1)
- [WiFiAwareServices](https://developer.apple.com/documentation/bundleresources/information-property-list/wifiawareservices?changes=__1_9)
- [Network](https://developer.apple.com/documentation/network)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
