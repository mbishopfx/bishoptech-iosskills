# SwiftUI Wi-Fi Aware and device-discovery proof matrix

This matrix defines what each kind of evidence can prove for an iOS 26 route
that combines Wi-Fi Aware, DeviceDiscoveryUI, AccessorySetupKit, and Network
Framework. A compile result proves a type relationship. It does not prove a
radio, pairing, accessory, permission, identity, or release claim.

Related route pages:

- [Wi-Fi Aware, DeviceDiscoveryUI, and AccessorySetupKit deep dive](../42-framework-deep-dives/140-swiftui-wifi-aware-device-discovery-route.md)
- [Route design](../21-design-deep-dives/168-swiftui-wifi-aware-device-discovery-route-design.md)
- [Capability recipe](../50-capability-recipes/171-swiftui-wifi-aware-device-discovery-route.md)
- [Compile-sized recipes](../70-code-recipes/183-swiftui-wifi-aware-device-discovery-recipes.md)

## Evidence vocabulary

| Evidence level | Can prove | Cannot prove |
| --- | --- | --- |
| Source and target inspection | Intended API, availability, entitlement/property-list shape, target membership, declared service role | A signed artifact contains the values, hardware supports the route, or user flow reaches the system surface |
| Swift typecheck | Imports, generic provider/endpoint relationships, availability annotations, callback signatures | Linker behavior, entitlement validity, radio behavior, picker presentation, accessory advertisement, or semantic correctness |
| Unit/reducer test | State transitions, stale-epoch rejection, bounded error mapping, idempotency and review rules | Wi-Fi Aware radio, system pairing, actual accessory setup, physical accessibility, or release packaging |
| SwiftUI UI test/simulator | Labels, fallback views, focus, Dynamic Type, cancellation projection, deterministic fixtures | Real peer discovery, pairing, hardware capabilities, accessory data path, physical haptics/radio, or signed entitlements |
| Signed archive inspection | Embedded entitlements, Info.plist, target membership, deployment target, extension resources, build identity | A TestFlight installation, supported hardware, system picker behavior, physical transport, or App Store production delivery |
| Physical two-device run | Real DeviceDiscoveryUI pairing, Wi-Fi Aware service visibility, Network listener/browser/connection, app handshake, bounded receipt | Every supported hardware family, accessory setup, future OS behavior, accessibility across all settings, or release metadata |
| Physical accessory run | Real AccessorySetupKit advertisement, picker match, authorization, removal/rename, Wi-Fi Aware/Bluetooth/Network path | Another vendor’s hardware, all firmware versions, App Store review, or an app-peer relationship |
| TestFlight/system run | Signed distribution artifact, target configuration in the installed build, picker/setup reachability, system integration | Universal hardware compatibility, all privacy states, source-level correctness, or production-scale operations |

## Route contract

The route is only considered end to end when this chain is observed:

~~~text
capability and configuration
  -> user-triggered system pairing/setup UI
  -> selected peer or authorized accessory
  -> Network Framework data path
  -> app-owned identity and protocol handshake
  -> approved operation
  -> validated and applied result
  -> explicit receipt and recoverable teardown
~~~

Do not collapse “picker returned,” “connection ready,” “bytes sent,” and
“operation applied” into one success Boolean.

## Configuration and availability matrix

| Case | Evidence to capture | Pass condition | Failing claim to avoid |
| --- | --- | --- | --- |
| Deployment and SDK | Xcode target settings, installed SDK, compiler availability diagnostics | Wi-Fi Aware symbols compile behind iOS 26 availability; iOS 26.4-only shared-secret path is gated separately | “All iOS 26 devices support the route” |
| Hardware floor | Apple-supported device list plus actual device model/OS | Product matrix names tested device pairs and the route’s minimum hardware | “The simulator represents the radio” |
| Wi-Fi Aware entitlement | Signed archive entitlements | `com.apple.developer.wifi-aware` contains only the intended `Publish`/`Subscribe` roles | “The import proves entitlement” |
| Service declaration | Built Info.plist and code lookup | Every intended service name and role matches `WiFiAwareServices` and `allServices` | “The picker can repair a bad declaration” |
| Accessory technologies | Signed app target and Info.plist | `NSAccessorySetupKitSupports` and Bluetooth arrays match the accessory’s actual advertisement | “AccessorySetupKit discovers any accessory” |
| Availability fallback | UI test on unsupported fixture and physical unsupported target if available | User receives a usable alternate route and no dead system button | “No devices means unsupported hardware” |
| iOS support environment | Installed `_DeviceDiscoveryUI_SwiftUI` interface and target compile | iOS code does not depend on the tvOS-only `devicePickerSupports` property; fallback is explicit | “The documentation example is portable to every platform” |

## App-to-app physical matrix

Use two supported iOS/iPadOS devices with the same signed TestFlight build or
the intended compatible build pair. Record model, OS, build, entitlement
digest, service revision, and a redacted attempt epoch.

| Scenario | Steps | Expected evidence |
| --- | --- | --- |
| Publisher becomes discoverable | Device A opens the user action and invokes `DevicePairingView`; Device B opens the subscriber route | System pairing UI appears only after explicit action; publisher state becomes advertising; no raw identity is shown as trusted |
| Subscriber selects a device | Device B invokes `DevicePicker`, selects Device A, and returns to the app | A typed endpoint is received; the review state identifies the selected relationship and scope |
| Supported service mismatch | Use a build with a different declared service or role | The route fails as a configuration/service state; it does not connect to an arbitrary service |
| App handshake | After Network connection, exchange protocol revision, nonce, app identity, service role, and capability set | Only the allowlisted peer/build reaches authenticated state; a transport-ready state alone is insufficient |
| Approved transfer | User reviews a file or command and confirms | Sender records bytes accepted; receiver validates and applies; receiver returns an application receipt with operation ID |
| User cancellation | Cancel from the system picker, review sheet, and connecting state | Browser/listener/connection tasks end; no stale callback starts a new operation; focus lands on recovery |
| Peer leaves | Lock or move one device out of range during discovery and transport | State becomes peer-lost/waiting; no automatic irreversible command is replayed |
| Radio resources unavailable | Run while the device reports temporary Wi-Fi Aware resource exhaustion | User sees a bounded retry state; no infinite retry loop or identity reset |
| Idle timeout/termination | Wait for or induce a Wi-Fi Aware timeout/termination | Error maps to a distinct recovery state and a new attempt gets a new handshake epoch |
| Background or screen lock | Lock, background, and return at each stage supported by the product | The product either resumes with documented state or clearly asks the user to restart; no false applied state |
| Wrong peer/build | Select a similarly named or incompatible app peer | App-owned handshake rejects it before the side effect; display name is not treated as proof |

## Accessory physical matrix

Use at least one real accessory whose advertisement and firmware match the
descriptor. Keep accessory and app logs separate, and do not record secrets or
raw personal identifiers.

| Scenario | Steps | Expected evidence |
| --- | --- | --- |
| Session activation | Create and retain `ASAccessorySession`; activate; wait for `activated` event | One active session and one event owner; session is not reused after invalidation |
| Picker match | Present an `ASPickerDisplayItem` with Wi-Fi Aware service name and correct role | Intended accessory appears with the product image/name; an unrelated accessory does not match |
| User cancellation | Dismiss the system picker | Completion/event state records user cancellation; no unauthorized accessory control appears |
| Authorization | Select accessory and complete the system setup path | `ASAccessory.state` transitions to authorized before controls unlock |
| Partial setup | Exercise awaiting authorization and either finish or fail authorization | UI explains the pending step; failure does not look authorized and leaves recovery |
| Accessory removal | Remove the accessory from system state or product flow | `accessoryRemoved` invalidates cached domain state and disables controls |
| Rename/change | Rename or change accessory metadata | UI updates presentation without changing app identity; capability projection is re-read |
| Wi-Fi Aware bridge | Read `wifiAwarePairedDeviceID`, correlate to `WAPairedDevice`, connect via Network | Correlation is explicit and authorization remains required; IDs are not displayed as identity |
| SSID upgrade | Offer `updateAuthorization(for:descriptor:)` for an existing accessory | Decline preserves the old route when supported; success creates a new verified capability state |
| Data-path failure | Disconnect the accessory after authorization | The authorized record remains visible but controls show unavailable; reconnect requires current capability and handshake checks |

## Security and authorization matrix

| Risk | Test | Pass condition |
| --- | --- | --- |
| Display-name spoofing | Use two peers/accessories with similar names | App identity and protocol handshake, not the name, decides authorization |
| Stale endpoint | Reuse a saved endpoint after a new pairing attempt | Epoch or endpoint binding rejects it and asks for a fresh selection |
| Replay | Replay a prior handshake or operation envelope | Nonce, epoch, expiry, and idempotency policy rejects or safely deduplicates it |
| Capability confusion | Peer advertises an unsupported operation | Allowlist rejects it before the control or document mutation |
| Scope confusion | Change selected file/command after review | Operation ID and reviewed scope no longer match; send is blocked |
| Transport-only success | Drop receiver application acknowledgment | Sender remains “waiting for application” or failed, never “applied” |
| Secret exposure | Inspect logs, service declarations, picker labels, AI input, and crash fixtures | No access token, shared secret, raw user content, or unnecessary identifier is exposed |
| Accessory authorization bypass | Invoke a control while accessory state is awaiting authorization | Deterministic gate blocks the operation and offers setup recovery |
| AI authority escalation | Return a model proposal that chooses a peer or calls setup | Model output is a proposal only; deterministic checks and user review remain required |

## SwiftUI, accessibility, and interaction matrix

| Test | Evidence | Pass condition |
| --- | --- | --- |
| Dynamic Type | UI screenshots/video at largest supported sizes | Identity, trust, status, and recovery remain readable; no clipped primary action |
| VoiceOver | Task run from intent through picker dismissal and recovery | Focus order and announcements identify relationship, state, scope, and next action |
| Voice Control | Voice commands for add, choose, review, cancel, retry | Each critical action has a unique spoken label |
| Switch Control | Traversal through candidate/review/recovery states | No action is reachable only by gesture or visual position |
| Keyboard/pointer | iPad keyboard and pointer run | Focus, submit, cancel, and system-sheet return are coherent |
| Reduce Motion | Pairing, reconnect, and loss transitions | Meaning survives without animation; no state is implied only by movement |
| Reduce Transparency | Glass shell and fallback | The same semantic grouping and trust distinction remains legible |
| Unsupported path | Capability failure and system-picker fallback | The user receives a useful alternate method and no misleading glass control |
| AI unavailable | Disable model or remove model fixture | Complete deterministic route remains available |

## Release and artifact matrix

| Artifact/check | Proof |
| --- | --- |
| Source | New pages link to official Apple/Swift sources; local links resolve; no nonofficial Markdown destinations |
| Compile | Recipe fences parse and typecheck against the installed iOS 26.4 simulator SDK; availability diagnostics are intentional |
| Archive | Entitlements and Info.plist are extracted from the signed archive; target membership is verified |
| TestFlight | The distributed build presents the picker/setup UI and carries the same service/configuration values as the archive |
| Physical peer | Two supported devices complete pairing, Network transport, handshake, receipt, cancellation, and reconnect |
| Physical accessory | Real hardware completes discovery, authorization, removal, Wi-Fi Aware or alternate data path, and side-effect proof |
| Privacy | Feature explanation and any relevant usage descriptions accurately describe the actual route; no unsupported local-network claim is added |
| Accessibility | Assistive-technology task run is completed on the signed build, not only a preview or simulator fixture |
| Distribution | App Store/TestFlight metadata and review notes match the real peer/accessory behavior and fallback |

## Evidence record template

Use a redacted record for each physical run:

~~~text
runID:
date:
deviceA: model / OS / build
deviceB-or-accessory: model / firmware / OS
archiveDigest:
wifiAwareRoles:
serviceRevision:
route: app-peer | accessory | ssid-upgrade
attemptEpoch:
permission/capability states:
system picker result:
handshake result:
operation ID:
application receipt:
cancellation/recovery result:
accessibility setting:
known limitations:
~~~

Do not attach raw Wi-Fi Aware IDs, endpoint addresses, shared secrets, user
documents, or accessory credentials to a routine evidence record.

## Sources

- [Wi-Fi Aware](https://developer.apple.com/documentation/wifiaware)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice](https://developer.apple.com/documentation/wifiaware/wapaireddevice)
- [WAPublisherListener](https://developer.apple.com/documentation/wifiaware/wapublisherlistener)
- [WASubscriberBrowser](https://developer.apple.com/documentation/wifiaware/wasubscriberbrowser)
- [WAPath](https://developer.apple.com/documentation/wifiaware/wapath)
- [WAError](https://developer.apple.com/documentation/wifiaware/waerror)
- [Network](https://developer.apple.com/documentation/network)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkBrowser](https://developer.apple.com/documentation/network/networkbrowser)
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
- [ASAccessoryEvent](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryevent)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
