# SwiftUI Wi-Fi Aware and accessory-discovery capability recipe

Use this recipe when the product outcome is “connect this iOS app to another
nearby app” or “add and control this Wi-Fi Aware accessory.” It turns the
framework route into a build order with explicit gates. The code recipes
paired with this page are compile-sized examples; this page is the product
composition and acceptance contract.

Related pages:

- [Wi-Fi Aware, DeviceDiscoveryUI, and AccessorySetupKit deep dive](../42-framework-deep-dives/140-swiftui-wifi-aware-device-discovery-route.md)
- [Nearby route design](../21-design-deep-dives/168-swiftui-wifi-aware-device-discovery-route-design.md)
- [Wi-Fi Aware and device-discovery recipes](../70-code-recipes/183-swiftui-wifi-aware-device-discovery-recipes.md)
- [Wi-Fi Aware and device-discovery proof matrix](../60-verification/165-swiftui-wifi-aware-device-discovery-proof-matrix.md)

## Outcome and lane selection

Write one of these in the product brief before adding a framework:

~~~text
App peer:
  A person selects another copy of this app and approves one scoped operation.

Hardware accessory:
  A person adds a physical product, authorizes it, and then uses its controls.

SSID upgrade:
  An existing authorized accessory is offered a separate Wi-Fi Aware upgrade.
~~~

If the brief says “nearby devices” without naming the relationship, stop and
resolve it. App peers use DeviceDiscoveryUI. Hardware setup uses
AccessorySetupKit. The data path after setup may be Wi-Fi Aware plus Network
Framework, but the picker and authorization state are not interchangeable.

## Recipe map

~~~text
1. Capability and deployment gate
2. Entitlement and service declarations
3. Peer/accessory identity model
4. System pairing or setup UI
5. Network Framework transport
6. App-owned handshake and operation scope
7. Cancellation, loss, and reconnection
8. SwiftUI/Liquid Glass projection
9. Optional typed on-device explanation
10. Physical-device and release evidence
~~~

Every stage produces a state that the next stage can verify. Do not jump from
stage 4 directly to a side effect because a picker returned an endpoint or an
accessory event delivered an object.

## 1. Gate the capability

For iOS 26, use `WACapabilities.supportedFeatures` and the installed SDK’s
availability annotations. Also read the maximum connection/service limits.
The screen should distinguish:

~~~text
unsupported hardware
missing signed entitlement
malformed or missing service declaration
no paired devices
temporary radio-resource exhaustion
user cancellation
~~~

Only the first and last are normal user states. A missing entitlement or bad
service declaration is a developer/release configuration failure; log a
redacted diagnostic and keep a fallback route rather than instructing the user
to repair the build.

The supported-device list in Apple’s Wi-Fi Aware documentation is a starting
matrix, not a substitute for physical testing. Do not claim “works on iOS 26”
from a simulator run.

## 2. Configure the target exactly once

For an app peer, configure:

~~~text
Entitlements
  com.apple.developer.wifi-aware = [Publish, Subscribe] as needed

Info.plist
  WiFiAwareServices = {
    _bishop-sync._tcp = {
      Publishable = true
      Subscribable = true
    }
  }
~~~

Use only the service roles the target owns. The publisher target might need
`Publish`; a subscriber-only target might need `Subscribe`. Keep the full
service name stable across both builds and validate the name against Apple’s
Wi-Fi Aware service naming rules.

For an accessory target, add `NSAccessorySetupKitSupports` with the actual
technology and, when Bluetooth is used, the required Bluetooth discovery
arrays. Do not place those declarations only in an extension when the
container app presents the picker. Verify target membership in the built
archive.

Acceptance checks:

- the signed archive contains the intended `Publish`/`Subscribe` values;
- the service declaration is present in the target that presents the pairing
  UI;
- the code’s `allServices` lookup succeeds for every declared role;
- AccessorySetupKit’s technology declarations match the accessory’s actual
  advertisement;
- no unneeded local-network/Bonjour declarations are added merely because the
  product uses Wi-Fi Aware; add those only when another route actually uses
  local-network/Bonjour discovery.

## 3. Model identity separately from presentation

Create a domain record that does not make a device name authoritative:

~~~text
NearbyCandidate
  localID: app-owned local record ID
  relationship: appPeer | accessory
  displayName: safe presentation string
  waPairedDeviceID: optional WAPairedDevice.ID
  accessoryID: optional ASAccessory identity
  serviceRole: publisher | subscriber
  protocolRevision: allowlisted value
  trust: unknown | selected | authenticated | blocked
  authorization: notApplicable | pending | authorized | denied
  observedAt: local timestamp
~~~

`WAPairedDevice.PairingInfo` is useful for pre-pair display but is not
authentication. `ASAccessory.displayName`, Bluetooth names, vendor names, and
model names are presentation or matching data. Resolve the app-owned identity
after transport connection and bind it to the current session epoch.

## 4. App-peer pairing path

The publisher exposes a user-triggered `DevicePairingView` with a
`WAPublisherListener` provider. The subscriber exposes a `DevicePicker` with a
`WASubscriberBrowser` provider. Both controls need a fallback view.

Publisher composition:

~~~text
WACapabilities.supportedFeatures
  -> WAPublishableService.allServices[declaredName]
  -> WAPublisherListener.wifiAware(.connecting(to: service, from: devices))
  -> DevicePairingView
  -> selected connection state
~~~

Subscriber composition:

~~~text
WACapabilities.supportedFeatures
  -> WASubscribableService.allServices[declaredName]
  -> WASubscriberBrowser.wifiAware(.connecting(to: devices, from: service))
  -> DevicePicker
  -> WAEndpoint
  -> review state
~~~

Use `.selected(...)` or `.userSpecifiedDevices` when the product needs
explicit scope. `.allPairedDevices` is convenient but should not silently
expand the user’s intended audience. The system picker’s selected endpoint
still needs app-owned identity and authorization checks.

The installed iOS SwiftUI interface does not expose the documented
`devicePickerSupports` environment value as an iOS-available property. Do not
copy the tvOS environment example into an iOS target. Use the provider and
framework availability checks that compile for the target, and always supply a
SwiftUI fallback.

## 5. Accessory setup path

Create a retained `ASAccessorySession`, activate it on a dedicated queue, and
project its events to the main actor. The setup state machine is:

~~~text
sessionCreated
  -> activateRequested
  -> activated
  -> pickerPresented
  -> accessoryDiscovered / accessoryAdded
  -> awaitingAuthorization
  -> authorized
  -> connected
~~~

The session is unusable after `invalidate()`. Treat it as an owned resource,
not a global singleton that can be silently restarted after invalidation.

For a manually described accessory:

1. Build an `ASDiscoveryDescriptor`.
2. Set the Wi-Fi Aware service name and publisher/subscriber role for the
   accessory’s actual behavior.
3. Build an `ASPickerDisplayItem` with a truthful product name and image.
4. Present `showPicker(for:completionHandler:)` from the user action after the
   session has activated.
5. Handle picker presentation/dismissal, accessory added/changed/removed, and
   errors in the event handler.
6. Finish or fail authorization according to the accessory setup flow.
7. Connect through Wi-Fi Aware/Network or the accessory’s other supported
   technology only after the state is authorized.

For an SSID-based accessory, `updateAuthorization(for:descriptor:)` is a
separate iOS 26 upgrade route. Show a review, preserve the old route when
possible, and handle a user cancellation without deleting the accessory.

## 6. Build the Network data path

Use the provider as the discovery description and the modern Network API as
the transport:

~~~text
publisher
  WAPublisherListener -> NetworkListener<ApplicationProtocol>

subscriber
  WASubscriberBrowser -> NetworkBrowser -> WAEndpoint
  WAEndpoint -> NetworkConnection<ApplicationProtocol>
~~~

For sensitive data, choose an encrypted protocol stack such as TLS over TCP.
If the product uses a Codable message layer, include:

~~~text
Envelope
  schemaRevision
  messageID
  correlationID
  sessionEpoch
  operationID
  kind
  boundedPayload
~~~

On iOS 26.4, investigate `NetworkConnection.wifiAware` and
`deriveSharedSecret` for route-specific key material. Record the protocol
name, derivation method, context, and key lifetime. Never store or log the raw
secret. Pairing and link encryption do not authorize an arbitrary domain
command.

Use `WAPath.performance` only for current diagnostics and adaptive policy.
Treat `WAError` and `NWError.wifiAware` as typed failure inputs. Do not
auto-retry indefinitely when the error indicates an invalid declaration,
missing entitlement, explicit termination, or a rejected app handshake.

## 7. Handshake and operation review

Immediately after the Network connection reaches the usable state, exchange a
small app-owned handshake:

~~~text
app identity / build family
protocol revision
session nonce
selected service role
paired-device or accessory correlation
supported capability set
requested operation scope
~~~

The peer replies with its identity, protocol revision, nonce binding, and
allowlisted capabilities. Only then should the SwiftUI projection enable the
operation button. Before a side effect, require explicit user review of the
target and scope. Use idempotency keys and application receipts.

For a document transfer, distinguish:

~~~text
send requested
bytes accepted
message decoded
content validated
content applied
application receipt received
~~~

For accessory control, distinguish “command sent” from “accessory reported
the requested state.” A model-generated command never bypasses this boundary.

## 8. Cancellation, loss, and reconnect

Give every browsing, pairing, setup, and transport attempt an epoch and a
cancel handle:

~~~text
attemptEpoch += 1
cancel old browser/listener/connection tasks
start new route task
ignore callbacks from older epochs
on loss: preserve approved scope but require a new handshake
on reconnect: re-read accessory/paired state and capabilities
~~~

Cancel the underlying async sequence or Network operation when the screen
leaves, not just the SwiftUI task that displays it. On `ASAccessorySession`,
stop presenting the picker before tearing down the owning coordinator. On
retry, use bounded exponential backoff and a user-visible retry state.

Never resume an irreversible command automatically after a peer loss. Resume a
versioned, idempotent document chunk or re-query accessory state only when the
product contract permits it.

## 9. Native design and accessibility acceptance

Use Liquid Glass for compact app-owned action groups and status controls. Keep
the identity, trust, authorization, error, and operation scope on a stable
content layer. The route must remain complete without glass, without AI, and
without an unavailable system picker.

Accessibility acceptance:

- all actions have semantic labels and hints;
- device/accessory identity and trust state are read together;
- state changes are announced without flooding VoiceOver;
- focus returns to the review or recovery action after picker dismissal;
- Dynamic Type, Increase Contrast, Reduce Motion, and Reduce Transparency
  preserve the state distinctions;
- keyboard, pointer, Voice Control, and Switch Control can start, cancel, and
  recover the route;
- no name, icon, animation, glass tint, or signal metric is the only identity
  or availability cue.

## 10. Optional on-device explanation

Use Foundation Models only after the deterministic layer has created a small,
redacted observation:

~~~text
EligibleCandidate
  relationship = appPeer
  paired = true
  serviceRole = subscriber
  protocolRevision = 2
  operation = document-transfer
  userSelected = true
~~~

Ask the model for a typed explanation or comparison, not a raw endpoint or a
tool call. Render the result as “On-device explanation,” show source fields,
and let the user approve the actual operation. Store the model and input
revision if auditability matters. If the model is unavailable, omit this layer
without changing the route.

## 11. Evidence gates

Do not call the capability shipped until the evidence matrix has each required
level:

~~~text
source/config
  entitlement, Info.plist, target membership, deployment and availability

compile
  imports, provider types, UIKit/SwiftUI bridges, actor/sendability review

simulator
  reducer, fallback, cancellation, stale-epoch, and message fixtures

physical app pair
  two supported devices, system pairing UI, Network path, handshake, receipt

physical accessory
  real advertisement, setup picker, authorization, removal, data path, state

signed release
  archive entitlements, TestFlight install, system picker, privacy copy,
  accessibility, reconnect, and no-debug-only assumptions
~~~

The final proof must include the negative paths: unsupported device,
entitlement/declaration error, user cancellation, no paired devices, no radio
resources, peer loss, accessory removal, authorization denial, app-handshake
rejection, idle timeout, and model unavailable.

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
- [Network Framework modern peer-transport route](../42-framework-deep-dives/139-swiftui-network-framework-modern-peer-transport-route.md)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
- [AccessorySetupKit](https://developer.apple.com/documentation/accessorysetupkit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessory](https://developer.apple.com/documentation/accessorysetupkit/asaccessory)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [AccessorySetupKit discovery declarations](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
