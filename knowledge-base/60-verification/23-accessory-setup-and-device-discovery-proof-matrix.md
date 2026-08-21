# AccessorySetupKit and DeviceDiscoveryUI proof matrix

Use this matrix to separate a picker preview from a physical accessory setup, and a selected endpoint from a trusted command path. Record the target, SDK, OS, accessory model/firmware, radio state, account state, and exact user actions.

## Evidence levels

| Level | Can prove | Cannot prove by itself |
| --- | --- | --- |
| Documentation | API roles, supported system boundaries, Info.plist/entitlement requirements, and stated platform caveats | Project configuration, physical matching, protocol safety, or release delivery |
| Source/compile | State model, descriptor validation, protocol types, target imports, and conditional availability | Picker invocation, pairing, radio behavior, encryption, accessory firmware, or physical effect |
| Preview/UI test | App-owned setup, detail, command review, fallback, and accessibility identifiers | System picker, real discovery, endpoint selection, accessory authorization, or physical command |
| Simulator | Layout, protocol fixtures, app lifecycle, some fallback states | Real Bluetooth/Wi-Fi/Wi-Fi Aware discovery, PIN pairing, radio loss, physical accessory, or thermal behavior |
| Signed physical device | Picker, pairing, selected accessory/endpoint, entitlements, radio, and selected hardware path | All device families, every firmware, long-run reliability, distribution entitlement approval |
| TestFlight/release | Distribution artifact and selected system path | Universal accessory compatibility, all network/account environments, or safety of an untested command |

## AccessorySetupKit configuration matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| AccessorySetupKit import/availability | Build named iOS/iPadOS target with current SDK | Wrong deployment target, unavailable framework, unsupported platform | Framework is available in this target |
| NSAccessorySetupSupports | Inspect source and built Info.plist | Wrong key/spelling, missing Bluetooth/WiFi value | System has the declared technology scope |
| Bluetooth company/name/service declarations | Compare plist with descriptor and accessory advertisement | Mismatch, broad filter, missing identifier | Descriptor can match the declared product route |
| Wi-Fi SSID/prefix declaration | Physical Wi-Fi accessory and built Info | Both SSID and prefix, wrong full/prefix semantics, stale network | Wi-Fi discovery declaration for tested accessory |
| Wi-Fi Aware descriptor | Wi-Fi Aware-capable accessory/device and current SDK | Unsupported property, wrong role/name | Descriptor represents the intended service |
| Target capability and signing | Inspect signed app entitlements/profile | Development works but distribution unavailable | Selected artifact is provisioned |
| Product image/name | Picker run with each supported variant | Wrong image, misleading name, localization overflow | Picker presentation for tested assets |
| ASAccessorySession activation | Physical device event log | No callback, invalidated session, wrong queue | Session activated for this target |
| Event handler queue | Concurrency test and serialized event log | Reentrancy, UI update off main actor, event loss | Events are handled on the selected isolation path |
| Previously selected accessories | Re-launch and inspect session.accessories | External removal, rename, revocation | App reconciles the current list |

## Picker and event matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| showPicker display items | Physical picker run | Empty item list, invalid descriptor, picker error | System picker presentation was attempted |
| Descriptor matching | Multiple similar accessories and negative accessory | Wrong service UUID, data mask mismatch, false positive | Matching behavior for tested advertisements |
| Immediate range | Accessories at near/far distances | RSSI variation, obstruction, multiple matches | Range filter behavior in the tested environment |
| accessoryDiscovered filtering | filterDiscoveryResults run | No acceptable item, custom image delay, timeout | App-filtered picker route for this accessory set |
| updatePicker | Physical run with discovered display item | Update error, duplicate display, stale picker | Updated picker state for tested items |
| finishPickerDiscovery | No-match and retry run | Timeout misrepresented, retry too soon | Empty discovery path returns clearly |
| pickerDidPresent/dismiss | Presentation/cancel/selection run | App changes screen too early, duplicate dismissal | App-owned transition follows picker lifecycle |
| accessoryAdded | Select known accessory and log event | Selection canceled, accessory missing, wrong item | Selected accessory event for tested device |
| accessoryChanged | Rename or property change | External change, stale local row | App updates identity/config state |
| accessoryRemoved | Remove from system or app | Remove failure, stale transport | App stops using removed accessory |
| picker setup pairing/bridging/failure | Physical pairing/bridge run | PIN failure, unsupported hardware, timeout | Setup state shown for tested route |
| migrationComplete | Existing BLE/Wi-Fi record migration | Duplicate, wrong peripheral identifier, old central initialized early | Migration path completed before legacy transport |
| AccessorySession invalidated | Trigger invalidation and relaunch | Session reused after invalidation | Recovery creates a valid new session |

## Post-setup transport matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Core Bluetooth transport | Physical BLE accessory with GATT fixture | Radio off, unauthorized, reset, service missing | BLE connection and schema for selected hardware |
| Network transport | Signed peer/device connection with protocol log | Endpoint stale, network change, authentication failure | Network path for the tested endpoint |
| Wi-Fi Aware transport | Two supported devices/accessory with declared service | Unsupported feature, service mismatch, pairing failure | Wi-Fi Aware path for selected devices |
| HomeKit transport | Physical Home accessory and Home authorization | External Home app edit, accessory unavailable | HomeKit state for selected home/device |
| Nearby Interaction | Supported UWB peer/accessory and token exchange | Session suspension, invalid token, physical obstruction | Ranging behavior, not identity or trust |
| Protocol handshake | Version/capability/identity fixture and physical run | Version mismatch, malformed payload, replay, timeout | App-level trust state for tested protocol |
| Command idempotency | Repeated/duplicated request test | Retry sends action twice, timeout ambiguity | Safe retry behavior for selected command |
| Physical side effect | Readback before/after with user confirmation | Wrong target, stale state, device disconnect, partial result | Observed effect for tested hardware, not universal safety |

## DeviceDiscoveryUI matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| DevicePicker availability | Current support environment on each target | Unsupported platform, fallback not shown | Picker support observed on tested device |
| Full-screen presentation | Physical modal run | Embedded/partial presentation, cancellation | System picker used as intended |
| Label and fallback | UI/accessibility test on supported/unsupported fixture | Misleading purpose, fallback implies failure | Preflight copy is understandable |
| onSelect endpoint | Two physical app/device instances | User cancels, stale endpoint, selection mismatch | Endpoint returned by tested pairing flow |
| DDDevicePairingAccess | Temporary/permanent access route on selected SDK | Permission expectations wrong, removal missing | Access level observed for tested pair |
| DevicePairingView | Publisher/subscriber physical run | Publisher not discoverable, duplicate service | Advertising route for selected service |
| Pairing/PIN | Physical pairing with wrong/correct PIN | User cancel, mismatch, timeout | System pairing result for tested devices |
| Network connection | NWListener/NWConnection run after pairing | Path loss, reconnect, process termination | Transport lifecycle for selected pair |
| NSApplicationServices/tvOS | Apple TV 4K and supported iOS/watchOS target | Wrong platform, non-universal purchase, multiple devices | tvOS route for tested product configuration |
| iCloud/Family account visibility | Account/family configuration run | Wrong account, device not shown, privacy filtering | Device visibility under tested account rules |

## Wi-Fi Aware matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Wi-Fi Aware entitlement | Signed app and provisioning inspection | Entitlement missing, distribution unavailable | Target is provisioned for Wi-Fi Aware |
| WiFiAwareServices | Built Info.plist and both roles | Invalid service name, missing publish/subscribe role | Declared service is available to the target |
| WACapabilities | Physical support check | Empty feature set, max device/service limit | Host capabilities for selected hardware |
| Publishable service | WAPublisherListener physical run | Listener fails, service unavailable | Publisher route for tested service |
| Subscribable service | WASubscriberBrowser physical run | Browser cannot find service, wrong device | Subscriber route for tested service |
| DeviceDiscoveryUI pairing | Pairing UI and PIN flow | Unsupported peer, canceled pairing, stale pairing | Pairing result for tested pair |
| Network data path | Throughput/latency/cancel/disconnect fixture | Large payload, path loss, protocol framing | Performance and lifecycle for workload/device |
| Device list updates | Paired-device sequence run | Add/remove/revoke, process restart | App reflects the selected device list |

## Privacy, accessibility, and release matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Permission explanation | Preflight copy plus system picker | Broad/unclear request, user cannot cancel | Copy accurately frames selected route |
| Identifier minimization | Log/network/app-group audit | SSID, endpoint, advertisement, PIN leak | Audited build avoids unnecessary sensitive identifiers |
| Physical accessory image/name | Picker and large-text run | Misleading product, localization clipping | Tested assets remain accurate |
| VoiceOver | Task-based setup/pair/connect/remove run | State not announced, picker transition confusion | Tested tasks are accessible |
| Dynamic Type | Largest supported sizes | Button clipping, hidden remove/confirm | Tested app-owned surfaces adapt |
| Reduced effects/high contrast | Physical settings run | Glass hides state, motion indicates only status | Tested fallback remains understandable |
| Privacy on locked/shared surface | Lock Screen/system-surface review | Device name/command exposed | Tested surfaces follow policy |
| Battery/thermal | Release-style workload with duration | Scan loop, high throughput, high CPU, heat | Observation for selected workload/device |
| Distribution | TestFlight/archive/profile and entitlement record | Development-only capability, missing target | Selected artifact is distribution-ready for the tested route |

## AI matrix

| Boundary | Minimum evidence | Failure cases | Claim boundary |
| --- | --- | --- | --- |
| Device/service proposal | Typed fixture and ambiguity tests | Multiple same-name devices, stale target | Proposal identifies a candidate, not trust |
| Advertisement minimization | Prompt/input audit | Raw payload/SSID/identifier sent | Selected input scope is controlled |
| Protocol validation | Deterministic allowlist and capability test | Arbitrary command, unsupported feature | AI cannot bypass transport/schema checks |
| Human confirmation | UI/system action test | Auto-send, repeated action, stale readback | Side effect follows review |
| No-model fallback | Availability/cancellation fixture | Model unavailable blocks setup | Deterministic manual route works |

## Required evidence packet

- Target/SDK/OS/device/accessory/firmware.
- Info.plist declarations and signed entitlements.
- Picker display items and descriptors.
- Event timeline from activation through selection/dismissal.
- Pairing/authorization/transport/protocol state.
- Negative cases and recovery results.
- Screenshots/recording for system surfaces.
- Accessibility settings and task outcomes.
- Logs with identifiers and payloads redacted.
- AI proposal, validation, approval, and final command result.

## Sources

- [AccessorySetupKit](https://developer.apple.com/documentation/AccessorySetupKit)
- [Discovering and configuring accessories](https://developer.apple.com/documentation/accessorysetupkit/discovering-and-configuring-accessories)
- [ASAccessorySession](https://developer.apple.com/documentation/accessorysetupkit/asaccessorysession)
- [ASAccessoryEventType](https://developer.apple.com/documentation/accessorysetupkit/asaccessoryeventtype)
- [ASDiscoveryDescriptor](https://developer.apple.com/documentation/accessorysetupkit/asdiscoverydescriptor)
- [ASPickerDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/aspickerdisplayitem)
- [ASDiscoveredDisplayItem](https://developer.apple.com/documentation/accessorysetupkit/asdiscovereddisplayitem)
- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DDDevicePairingAccess](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess)
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
