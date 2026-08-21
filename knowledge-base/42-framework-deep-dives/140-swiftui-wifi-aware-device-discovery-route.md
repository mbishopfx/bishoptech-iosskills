# SwiftUI Wi-Fi Aware, DeviceDiscoveryUI, and AccessorySetupKit route

For an iOS 26 app that needs a nearby device without depending on an internet
connection, start by choosing the relationship you are actually building:

~~~text
app to app
  -> Wi-Fi Aware service declaration and entitlement
  -> DeviceDiscoveryUI pairing UI
  -> WAPairedDevice / WA service identity
  -> Network Framework listener, browser, and connection
  -> app-owned handshake and typed messages

app to hardware accessory
  -> AccessorySetupKit descriptor and system picker
  -> ASAccessorySession lifecycle and authorization events
  -> ASAccessory identity and technology bridge
  -> Wi-Fi Aware or Core Bluetooth / Network data path
  -> accessory protocol and user-approved side effects
~~~

Wi-Fi Aware is not the same thing as MultipeerConnectivity, Bonjour on the
local network, or the `peerToPeerIncluded` Network Framework option. It is a
Wi-Fi Alliance neighbor-awareness route exposed by Apple for supported iOS
and iPadOS devices. It establishes a peer-to-peer Wi-Fi path without an
infrastructure access point, can coexist with infrastructure Wi-Fi, and uses
pairing plus a declared service to decide which endpoints can participate.
Network Framework carries the application protocol after discovery. Keep
those responsibilities separate in the architecture and in the UI.

## Choose the lane before writing code

| Desired relationship | First route | What the route owns | What the app still owns |
| --- | --- | --- | --- |
| Two copies of the app exchange a file, document, game state, or local command | DeviceDiscoveryUI + WiFiAware + Network | Secure system pairing UI, Wi-Fi Aware peer path, service discovery, typed Network connection | Service contract, app identity, authorization, protocol version, framing, receipts, cancellation, and SwiftUI state |
| A person adds a physical accessory | AccessorySetupKit | Privacy-preserving accessory discovery, picker display, setup authorization, rename/remove, accessory list | Accessory protocol, firmware compatibility, identity correlation, control authorization, and the post-setup data path |
| A previously configured Wi-Fi accessory gains Wi-Fi Aware support | AccessorySetupKit `updateAuthorization` + WiFiAware | System-mediated technology upgrade and paired-device association | Explain the upgrade, revalidate the accessory, migrate capability state, and handle cancellation or denial |
| An older product already uses MCSession | MultipeerConnectivity only as a compatibility lane | Legacy peer session and delegate callbacks | Deprecation decision, migration boundary, identity, framing, and a real fallback if the modern route is unavailable |
| Devices are on the same managed network or need internet/cloud delivery | Network Framework/URLSession/Bonjour as appropriate | Network path and transport | Local-network privacy, server trust, authentication, offline policy, and application delivery |

Do not make AccessorySetupKit a generic app-peer browser. Do not make
DeviceDiscoveryUI a hardware setup protocol. Do not use a Wi-Fi Aware endpoint
or a display name as a durable account identity. Those mistakes create an app
that can look correct in a simulator while silently losing authorization and
recovery semantics on real devices.

## Availability and capability gates

The installed iOS 26.4 SDK exposes the primary Wi-Fi Aware symbols as iOS
26.0 APIs. The shared-secret bridge on `NetworkConnection.wifiAware` and
`WAConnection.deriveSharedSecret` is iOS 26.4. Wi-Fi Aware is unavailable on
macOS, Mac Catalyst, tvOS, watchOS, and visionOS in the installed interface.
DeviceDiscoveryUI has additional platform-specific availability, so check the
target SDK rather than copying a cross-platform sample into an iOS target.

Apple’s Wi-Fi Aware documentation lists support beginning with these device
families: iPhone 12 and later; iPad (10th generation and later); iPad Air
(4th generation and later); iPad Pro 11-inch (3rd generation and later);
iPad Pro 12.9-inch (5th generation and later); and iPad mini (6th generation
and later). Treat that list as a capability floor, not as proof that every
future hardware SKU or every simulator configuration supports the radio.
Gate the feature with:

~~~swift
@available(iOS 26.0, *)
func canOfferWiFiAware() -> Bool {
    WACapabilities.supportedFeatures.contains(.wifiAware)
}
~~~

Also inspect the advertised limits before presenting a feature that assumes a
particular topology:

- `WACapabilities.maximumConnectableDevices` limits simultaneous connection
  planning.
- `maximumPublishableServices` and `maximumSubscribableServices` constrain
  how many declared service roles the app can use.
- `WAError.noRadioResources` is a recoverable resource state, not an identity
  or permission result.
- The user’s Wi-Fi Aware pairing inventory is read through
  `WAPairedDevice.allDevices`, whose current snapshot and updates are
  asynchronous.

The Wi-Fi Aware capability is a target configuration boundary. The entitlement
is an array with one or both of the values `Publish` and `Subscribe` under
`com.apple.developer.wifi-aware`. Request only the role the app really uses,
then verify the signed archive’s entitlements. A source file that imports
`WiFiAware` does not prove the entitlement is present.

The declared service catalog is a second boundary. `WiFiAwareServices` is a
dictionary keyed by the full over-the-air service name. Each entry declares
whether the app is `Publishable`, `Subscribable`, or both. Service names follow
Apple’s documented service-name rules: use a valid DNS-SD-style name such as
`_bishop-sync._tcp`, keep each component within the documented length limit,
and keep the declaration, the peer’s role, and the code lookup identical.
Treat malformed or contradictory service declarations as configuration bugs;
do not attempt to “fix” them at runtime by accepting an arbitrary service.

For AccessorySetupKit, add the appropriate `NSAccessorySetupKitSupports`
array for the technologies the accessory actually exposes. If Bluetooth is
included, also supply the required Bluetooth company identifier, name, and
service declarations described by Apple. The picker and discovery behavior
depend on those target declarations. A missing or mismatched key can cause
discovery to fail or the system to reject the configuration before the app’s
domain code runs.

## Service and paired-device identity

`WAPublishableService` and `WASubscribableService` are typed views over the
service names declared in the app’s property list. Apple’s sample turns a
declared name into a product-level static property:

~~~swift
@available(iOS 26.0, *)
extension WAPublishableService {
    static var fileService: WAPublishableService {
        allServices["_bishop-sync._tcp"]!
    }
}
~~~

Use a central constant in a real product and validate that the lookup is
non-nil during a configuration test. The static lookup is not a license to
accept arbitrary service strings from a peer.

`WAPairedDevice` provides an `id`, optional `name`, and optional `PairingInfo`.
The numeric ID is useful for local correlation, but it is still not a user
account, a cryptographic proof, or a permission to perform a side effect.
Apple describes `PairingInfo` as unauthenticated information received before
pairing. Keep it in a pre-pair presentation model. After pairing, perform an
app-owned handshake that binds the selected local record to the current
connection and the product’s trust record.

When the accessory route is involved, `ASAccessory.wifiAwarePairedDeviceID`
can bridge an authorized accessory to the Wi-Fi Aware paired-device ID. Treat
that as a correlation value supplied by the system, not as a reason to skip
the accessory’s authorization state or the app’s own identity checks. Keep
these values in separate fields:

~~~text
PeerRecord
  appPeerID: app-owned stable identity
  waPairedDeviceID: optional WAPairedDevice.ID
  accessoryID: optional ASAccessory identity
  trust: unknown | selected | authenticated | blocked
  displayName: presentation only
  capabilities: allowlisted and versioned
~~~

Never use the accessory’s display name, the Wi-Fi Aware pairing name, a
Bluetooth name, or a vendor/model string as authorization. Names can collide,
change, be truncated, or describe hardware rather than the app instance.

## Pairing UI: DeviceDiscoveryUI

DeviceDiscoveryUI supplies Apple’s pairing surface for app-to-app and
app-to-device peer relationships. Its SwiftUI controls are deliberately
system-like:

- `DevicePairingView` lets the local app become discoverable and advertise a
  listener provider from a user-triggered control.
- `DevicePicker` presents available devices and returns a typed provider
  endpoint through `onSelect`.
- `DDDevicePairingViewController` and `DDDevicePickerViewController` provide
  UIKit integration when a target has an existing controller hierarchy.
- `DDDevicePairingAccess.default` and `.permanent` describe the requested
  access lifetime. Make the lifetime a deliberate product decision and explain
  it before invoking system UI.

Apple’s current peer-to-peer sample uses a `WAPublisherListener` provider with
`DevicePairingView` and a `WASubscriberBrowser` provider with `DevicePicker`.
The system surface is not the data protocol. The selected `WAEndpoint` is the
input to a Network Framework connection; it is not an application receipt.

The pairing screen should be opened from an explicit nearby action. Keep the
pre-system label and fallback useful if the device cannot offer the route. On
iOS 26, do not rely on the `devicePickerSupports` SwiftUI environment value as
an iOS portability check: the installed `_DeviceDiscoveryUI_SwiftUI`
interface marks that environment property unavailable in iOS and exposes it
for tvOS. Use the provider’s and framework’s documented support checks in the
target you are compiling, and preserve a regular SwiftUI fallback view.

## Network Framework data path

The Wi-Fi Aware provider supplies the discovery semantics; Network Framework
owns the connection and protocol stack. The shape is:

~~~text
publisher
  WAPublisherListener.wifiAware(.connecting(to: service, from: devices))
  -> NetworkListener<ApplicationProtocol>

subscriber
  WASubscriberBrowser.wifiAware(.connecting(to: devices, from: service))
  -> NetworkBrowser<WASubscriberBrowser>
  -> WAEndpoint
  -> NetworkConnection<ApplicationProtocol>
~~~

Use `NetworkListener` for the publisher and `NetworkBrowser` for the
subscriber. The endpoint is a typed `Connectable` value, so a modern connection
can be constructed without converting it to an untyped socket. For the app
protocol, choose a stack that expresses the message contract:

~~~swift
@available(iOS 26.0, *)
func makeWiFiAwareConnection(to endpoint: WAEndpoint) -> NetworkConnection<TLS> {
    NetworkConnection(to: endpoint) {
        TLS { TCP() }
    }
}
~~~

For discrete domain messages, put `Coder` above TLS and include a schema
revision, message ID, and correlation ID. For a byte stream, bound a length
before allocating. For a high-rate route, measure `WAPath.performance` and
choose `WAParameters.realtime` or `.defaults` intentionally. Do not turn a
performance report into a promise about transfer latency; it is an observation
of the current path.

`NWParameters().wifiAware { ... }` can tune the Wi-Fi Aware performance mode.
Keep this choice in the transport coordinator and expose a user-facing label
only if it changes the product’s behavior. An “optimized” label is misleading
when the route is thermally constrained or the device has no radio resources.

On iOS 26.4, `NetworkConnection.wifiAware` exposes a `WAConnection` from which
the app can derive a `WASharedSecret` for TLS or IPsec with the documented
KDF. This can supply route-specific key material without inventing a second
pairing secret. It does not remove the need for an app identity, authorization
decision, replay protection, protocol version, and key-lifetime policy.

Map `NWError.wifiAware` to a domain error and preserve the reason. In
particular, distinguish unsupported hardware, missing entitlement, unavailable
radio resources, a service declaration problem, a paired device that has
disappeared, a timeout, a failed connection, an idle timeout, and an explicit
termination. The UI should not show all of those as “No devices found.”

## AccessorySetupKit is a different lifecycle

AccessorySetupKit is the system-mediated setup route for physical accessories.
It provides privacy-preserving discovery and a picker that uses app-provided
names, product images, and `ASDiscoveryDescriptor` filters. The descriptor can
match Bluetooth properties, an SSID or SSID prefix, or—on iOS 26—Wi-Fi Aware
service name, role, model name, and vendor name.

The minimum session lifecycle is:

~~~text
create ASAccessorySession
  -> activate(on:eventHandler:)
  -> wait for activated event
  -> showPicker(...) from an explicit user action
  -> receive picker and accessory events
  -> inspect ASAccessory.state
  -> finishAuthorization or failAuthorization when instructed
  -> connect using the technology-specific data path
  -> observe accessoryAdded/Changed/Removed
  -> invalidate on teardown; never reuse an invalidated session
~~~

`ASAccessorySession.accessories` is the system’s selected-accessory list. An
`ASAccessory` can be unauthorized, awaiting authorization, or authorized.
Only the authorized state should unlock the product’s post-setup controls, and
even then the app must verify the accessory’s current capabilities and
connection state.

For a Wi-Fi Aware accessory, configure `wifiAwareServiceName` and the correct
`wifiAwareServiceRole` on the descriptor before presenting the picker. For an
existing SSID-based accessory, iOS 26’s
`updateAuthorization(for:descriptor:completionHandler:)` can ask the system to
upgrade its technology authorization to Wi-Fi Aware. Treat an upgrade as a
separate review step: show what is changing, handle cancellation, and retain a
working authorized route if the user declines and the product supports one.

Use `ASPickerDisplayItem.setupOptions` for the system-supported rename,
confirmation, or “finish in app” moments. Do not simulate those screens in a
custom glass sheet when the system picker owns the decision. Use
`updatePicker(showing:completionHandler:)` and
`finishPickerDiscovery(completionHandler:)` only when the product has opted
into the documented manual filtering and unbounded discovery behavior; bound
the work and end it on screen dismissal or cancellation.

When an accessory is removed, renamed, or its descriptor changes, invalidate
the cached domain projection and require a fresh capability and authorization
read. Do not keep sending commands to a stale `ASAccessory` object because its
display name still appears in a SwiftUI list.

## A handshake remains necessary after pairing

Pairing reduces who can appear in a route. It does not define the app’s
authorization or the semantics of an operation. On every new connection:

~~~text
selected endpoint
  -> current path and transport state
  -> protocol version exchange
  -> app instance identity and nonce
  -> pair/accessory correlation check
  -> capability allowlist
  -> user-approved operation scope
  -> typed messages
  -> application receipt
~~~

Bind the handshake to the current session epoch and endpoint. Reject a stale
endpoint, reused nonce, unsupported protocol revision, unrecognized service
role, capability that the build does not implement, or an operation outside
the selected scope. Keep application receipts separate from transport sends:
“the bytes were accepted by Network Framework” is not “the peer validated and
applied the command.”

If the app controls an accessory, use a command envelope with an operation ID,
target accessory ID, capability revision, authorization epoch, expiry, and
idempotency key. The accessory or app can then reject replayed or late work.
For documents, use content hashes, bounded chunks, resumable revisions, and a
final application acknowledgment. Avoid transmitting secrets in service names,
device picker labels, TXT-like discovery metadata, or AI prompts.

## SwiftUI and Liquid Glass boundaries

The native setup controls already carry system visual language. Surround them
with a calm app-owned screen rather than re-creating the pairing sheet:

~~~text
intent and explanation
  -> DevicePairingView / DevicePicker / accessory picker action
  -> selected peer or accessory review
  -> handshake and capability status
  -> typed operation progress
  -> applied / cancelled / recoverable failure
~~~

Use Liquid Glass for functional grouping around the app-owned controls:

- a compact “Add device” or “Become discoverable” action group;
- a selected-device review toolbar;
- a connection-status group that can morph from connecting to cancel;
- a bounded accessory action group after authorization.

Keep discovery metadata, trust warnings, and recovery copy on an opaque,
legible content layer. Do not put every device row in glass, and do not use
glass opacity as the visual distinction between “seen,” “paired,” and
“authorized.” Use text, semantic state, and explicit labels. Under Reduce
Transparency or a platform without the effect, the same content and controls
must remain usable.

Keep the Wi-Fi Aware provider, AccessorySetupKit session, and Network objects
behind an actor or observable coordinator. The SwiftUI layer should receive a
small projection such as:

~~~text
NearbyRouteState
  capability: supported | unsupported | missingEntitlement | noResources
  pairing: idle | presenting | selected | cancelled | failed
  selectedPeer: reviewed presentation record?
  accessory: unauthorized | awaitingAuthorization | authorized | removed
  transport: idle | browsing | connecting | ready | waiting | failed
  operation: idle | proposed | awaitingReview | running | applied | cancelled
~~~

That projection prevents a stale `WAEndpoint`, a removed accessory, or an
unfinished AI proposal from appearing as an active control.

## Optional on-device AI lane

Foundation Models or another on-device model may help explain a verified
nearby option, summarize a transfer, or draft a human-readable pairing plan.
Treat it as a proposal layer:

~~~text
typed local observation
  -> model availability and input-size gate
  -> typed ConnectionProposal
  -> show source fields and uncertainty
  -> user reviews peer, scope, and side effect
  -> deterministic authorization and transport
~~~

Do not give the model the raw paired-device inventory, secrets, access tokens,
unbounded accessory advertisements, or a tool that can pair, authorize,
remove, rename, or send without review. A model may suggest “use the nearby
Mac for this transfer” only after the app has already computed the eligible
candidate set. The deterministic layer must enforce the device capability,
paired identity, service role, authorization epoch, operation scope, and
transport state.

Persist the model identifier, prompt/input revision, candidate-set revision,
proposal, user decision, and final operation ID when the product needs an
auditable history. If the on-device model is unavailable, show the same
candidate and setup flow without an AI explanation. AI availability must never
be the only way to finish pairing or operate an accessory.

## Accessibility and alternate input

Use the system picker’s labels and supplement the surrounding SwiftUI route:

- Give each custom action a short, stable label such as “Add nearby device” or
  “Stop searching.”
- Expose the selected peer’s display label, trust state, and operation scope as
  one accessible summary, not as unlabeled visual chips.
- Announce transitions such as “Device selected,” “Waiting for the other
  device,” “Pairing cancelled,” and “Transfer applied.”
- Do not rely on signal strength, glass tint, animation, or a radio-wave icon
  alone to communicate support or failure.
- Test Dynamic Type, VoiceOver focus after system-picker dismissal, Voice
  Control phrases, Switch Control traversal, keyboard/pointer selection on
  iPad, Bold Text, Increase Contrast, Reduce Motion, and Reduce Transparency.

If a peer disappears while the user is reviewing it, keep focus on the
recoverable status and offer “Search again” or “Choose another device.” Do not
silently move focus to a different peer or submit a different operation.

## Physical-device and release proof

The simulator can typecheck the route and exercise reducer states. It cannot
prove Wi-Fi Aware radio behavior, pairing, device picker presentation, an
accessory advertisement, or end-to-end hardware setup. The minimum physical
matrix is:

~~~text
two supported iOS/iPadOS devices
  publisher shows DevicePairingView
  subscriber shows DevicePicker
  user selects the intended device
  Network listener/browser/connection reaches the expected state
  app handshake authenticates the intended build and peer
  bounded typed transfer completes and is acknowledged

one supported device + real accessory
  AccessorySetupKit picker discovers the intended accessory
  display item and descriptor match
  cancellation and denial recover
  accessoryAdded/Changed/Removed update the projection
  Wi-Fi Aware or Bluetooth/Network data path connects
  authorized operation is applied and observable on the accessory
~~~

Repeat after a fresh install, with a revoked or missing entitlement in a
negative build, with radio resources unavailable, after the peer leaves, after
screen lock/background, after an accessory is renamed or removed, and after a
transport idle timeout. Capture event logs without raw identifiers or user
content.

The archive and TestFlight proof must separately show:

- signed entitlements contain the intended Wi-Fi Aware roles and no accidental
  broader capability;
- `WiFiAwareServices` and AccessorySetupKit declarations are in the correct
  app target and extension target boundaries;
- the deployment target and availability gates match the release artifact;
- the system picker and accessory session are reachable from the user flow;
- the physical two-device/accessory path works in the signed build, not only a
  Debug build;
- cancellation, denial, pairing removal, and reconnect leave no unauthorized
  retained operation;
- privacy copy, accessibility behavior, and App Review metadata describe the
  actual nearby/accessory feature.

## Sources

- [Wi-Fi Aware](https://developer.apple.com/documentation/wifiaware)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice](https://developer.apple.com/documentation/wifiaware/wapaireddevice)
- [WAPublishableService](https://developer.apple.com/documentation/wifiaware/wapublishableservice)
- [WASubscribableService](https://developer.apple.com/documentation/wifiaware/wasubscribableservice)
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [WAEndpoint](https://developer.apple.com/documentation/wifiaware/waendpoint)
- [WAPath](https://developer.apple.com/documentation/wifiaware/wapath)
- [WAConnection](https://developer.apple.com/documentation/wifiaware/waconnection)
- [WASharedSecret](https://developer.apple.com/documentation/wifiaware/washaredsecret)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [NWParameters](https://developer.apple.com/documentation/network/nwparameters)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DDDevicePairingViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingviewcontroller)
- [DDDevicePickerViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepickerviewcontroller)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessory](https://developer.apple.com/documentation/accessorysetupkit/asaccessory)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASPickerDisplaySettings](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplaysettings)
- [AccessorySetupKit discovery declarations](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [NSAccessorySetupBluetoothCompanyIdentifiers](https://developer.apple.com/documentation/bundleresources/information_property_list/nsaccessorysetupbluetoothcompanyidentifiers)
- [NSAccessorySetupBluetoothNames](https://developer.apple.com/documentation/bundleresources/information_property_list/nsaccessorysetupbluetoothnames)
- [NSAccessorySetupBluetoothServices](https://developer.apple.com/documentation/bundleresources/information_property_list/nsaccessorysetupbluetoothservices)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
