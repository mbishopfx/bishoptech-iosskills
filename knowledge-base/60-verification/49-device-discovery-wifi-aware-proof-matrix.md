# DeviceDiscoveryUI and Wi-Fi Aware proof matrix

This matrix prevents a local picker preview or a successful framework import from being mistaken for a working peer-to-peer feature. The route has at least four separate proofs:

1. target configuration and entitlement proof;
2. system pairing and access proof;
3. physical two-device transport proof;
4. application protocol and domain-result proof.

If the feature claims background behavior, persistent access, a media receiver, an accessory, or a release capability, add the corresponding system and distribution evidence.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| The target can use Wi-Fi Aware | Selected SDK compile plus signed com.apple.developer.wifi-aware entitlement | An import, source URL, or simulator |
| The declared service is valid | Merged/signed Info.plist contains WiFiAwareServices with valid service names and roles | A string in an unbuilt project file |
| The host supports the route | Physical-device WACapabilities result and recorded device/OS build | A model family assumption or an empty preview |
| DeviceDiscoveryUI can present | Physical system run of DevicePairingView or DevicePicker with the intended provider | A custom button or snapshot test |
| Access scope is correct | Run demonstrating default/permanent choice and product copy | A hard-coded enum value |
| Pairing completes | Two supported devices complete the system pairing dialog and each app observes its paired-device projection | A returned endpoint or picker dismissal |
| Paired devices update | WAPairedDevice.allDevices snapshots recorded after add, change, and remove | A cached local peer row |
| Publisher starts | NetworkListener reaches its ready/active state and accepts an inbound connection | Construction of a listener object |
| Subscriber browses | NetworkBrowser reports the declared service and approved device set | NWBrowser output from a different route |
| Connection is ready | NetworkConnection state reaches the target protocol’s ready state | A selected NWEndpoint |
| Messages arrive | Typed request/acknowledgement round trip with operation ID and payload limits | A send callback or byte count |
| Domain operation completes | Receiving domain writes a completed result and sender reconciles it | Transport acknowledgement |
| Retry is safe | Disconnect at each phase and repeat with idempotency/reconciliation | A successful first run |
| Background route works | Signed physical-device run under the claimed background mechanism with resource measurements | A foreground test or BackgroundTasks request |
| Security boundary holds | Unauthorized peer/command, stale ID, malformed payload, replay, and oversized payload are rejected | Wi-Fi-layer encryption alone |
| AI boundary holds | Proposal, deterministic resolution, user approval, validated command, and completion evidence are separately recorded | A model-generated device name |
| Accessibility holds | Task-based VoiceOver, Voice Control, Switch Control, Dynamic Type, Reduce Motion, and Reduce Transparency runs | Labels in source or a preview |
| Release route holds | Distribution-signed two-device run with approved capability, target membership, and metadata | A development entitlement or simulator |

## Target configuration record

Record one row per target:

| Field | Example value |
| --- | --- |
| App/extension target | Publisher app, subscriber app, or shared target |
| SDK/deployment | Selected Xcode SDK and minimum OS |
| Frameworks | DeviceDiscoveryUI, WiFiAware, Network, SwiftUI/UIKit |
| Wi-Fi Aware entitlement | Publish, Subscribe, or both |
| WiFiAwareServices | Exact fully qualified service names and roles |
| Pairing provider | Wi-Fi Aware, application service, or AccessorySetupKit |
| Access scope | default or permanent |
| Device support | WACapabilities result |
| Transport | NetworkListener/Browser/Connection or NWListener/NWConnection |
| Protocol | TCP, QUIC, UDP, TLS, coder/framer, version |
| Data policy | Payload classes, retention, redaction, deletion |
| Background claim | None or named platform runtime |

Inspect the built artifact. A project editor setting is not proof that the signed executable received the entitlement or merged Info.plist entry.

## Physical two-device test matrix

| ID | Setup | Action | Expected evidence |
| --- | --- | --- | --- |
| P01 | Two supported physical devices, same app version | Open publisher and subscriber pairing entry points | Both system surfaces appear with correct labels/fallbacks |
| P02 | Same as P01 | Pair the devices through DeviceDiscoveryUI | System pairing completes; peer appears in both app projections as designed |
| P03 | Paired devices | Remove access or forget the peer | Paired-device snapshot changes; stale local association is handled |
| P04 | Paired, publisher available | Start NetworkListener | Listener state and service publication are recorded |
| P05 | Paired, subscriber available | Run NetworkBrowser | Only the intended service/device set appears |
| P06 | Candidate endpoint | Select a peer and create NetworkConnection | Connection state reaches ready or produces a classified failure |
| P07 | Ready connection | Send a bounded request | Receiver decodes, validates, and returns acknowledgement |
| P08 | Accepted request | Complete domain action | Sender receives completed result distinct from accepted |
| P09 | Between send and ack | Kill or disconnect one side | Result becomes unknown/pending; retry does not duplicate mutation |
| P10 | Invalid protocol | Send wrong version, stale operation, or oversized payload | Receiver rejects without corrupting local state |
| P11 | Multiple peers | Pair more than one device within the supported limit | Selection and allowlist remain deterministic |
| P12 | Device/OS boundary | Repeat on the minimum supported physical device and current device | Availability and behavior differences are documented |

## Wi-Fi Aware performance evidence

Record the payload and environment:

- device models and OS builds;
- distance and obstruction;
- infrastructure Wi-Fi and cellular state;
- number of paired devices;
- service role and performance mode;
- protocol and message size;
- average and tail latency;
- loss/retry/duplicate rate;
- CPU, memory, battery, and thermal observations;
- foreground/background state;
- connection lifetime and teardown.

Use the Wi-Fi Aware performance information exposed through the current path when the selected SDK supports it. A single signal or latency reading is a measurement for that run, not a guarantee for all rooms, devices, or workloads.

## Access and privacy evidence

Verify:

- default access does not silently become a permanent peer;
- permanent access has a visible forget/revoke flow;
- device display names do not expose more personal data than needed;
- logs redact endpoints, pairing metadata, payloads, and secrets;
- the app remains useful when no device is paired;
- local data is retained or deleted according to an explicit policy when a peer disappears;
- an unknown peer cannot submit a valid business command solely because the transport is encrypted;
- the system picker is not replaced with an unbounded custom scanner;
- normal local-network permissions are not claimed or omitted based on assumptions from a different transport.

## Protocol and side-effect evidence

For each command, capture:

1. operation ID;
2. target device ID;
3. protocol version;
4. local approval event;
5. validation result;
6. send timestamp;
7. remote receipt/accepted acknowledgement;
8. remote domain completion or failure;
9. sender reconciliation;
10. retry or expiry result.

The domain owner should be the only writer of completed state. A transport layer can report delivery or acknowledgement but should not mark a file moved, a setting changed, or a purchase fulfilled unless the receiving domain confirms it.

## AI evidence

If a model helps with peer selection or commands, record:

- input facts and their freshness;
- the model output;
- candidate peer IDs considered;
- the deterministic resolution result;
- ambiguity or rejection reason;
- visible user confirmation;
- validated typed command;
- operation ID and acknowledgement;
- final domain state.

Test prompt injection through device names, service descriptions, received payloads, and peer-supplied metadata. Treat all of them as untrusted input. A model must not elevate a remote string into an instruction or an authorization.

## System-surface and accessibility evidence

Capture screenshots or recordings only as supporting evidence. The primary record should include:

- whether DevicePairingView/DevicePicker was system-owned;
- whether the picker was presented full-screen/modal as required;
- what the fallback showed;
- VoiceOver labels and announcements;
- Dynamic Type sizes tested;
- Reduce Motion and Reduce Transparency results;
- keyboard/pointer/Voice Control/Switch Control behavior where supported;
- error state and recovery copy;
- whether glass was limited to app-owned functional controls.

## Release evidence vocabulary

Use precise labels:

| Label | Meaning |
| --- | --- |
| source | Apple documentation and route design |
| compile | The selected target builds with the current SDK |
| simulator | The code ran in a simulated environment; radio/system claims remain unproven |
| signed device | The exact signed app ran on a physical device |
| system pairing | The system picker and pairing dialog completed |
| two-device | Two physical devices exchanged a protocol message |
| provider | Accessory, media receiver, account, or remote service participated |
| distribution | The distribution-signed artifact retained the required configuration |
| release | Store/TestFlight/production path was tested in its actual environment |

Never collapse these labels into “works.”

## Evidence record template

~~~yaml
route: DeviceDiscoveryUI-WiFiAware
build:
  app_version: ""
  build_number: ""
  sdk: ""
  deployment_target: ""
targets:
  - name: ""
    role: publisher-or-subscriber
    entitlement_values: []
    wifi_aware_services: []
devices:
  - model: ""
    os: ""
    wacapabilities: []
pairing:
  provider: DeviceDiscoveryUI
  access: default-or-permanent
  result: ""
transport:
  protocol: ""
  performance_mode: bulk-or-realtime
  listener_browser_connection: ""
  state_trace: []
protocol:
  operation_id: ""
  accepted: false
  completed: false
  retry_safe: false
accessibility:
  voiceover: ""
  dynamic_type: ""
  reduce_motion: ""
  reduce_transparency: ""
ai:
  used: false
  proposal: ""
  deterministic_resolution: ""
  user_approval: ""
release:
  signed_artifact: ""
  environment: ""
  result: ""
known_limits: []
~~~

## Sources

- [DeviceDiscoveryUI](https://developer.apple.com/documentation/devicediscoveryui)
- [DevicePairingView](https://developer.apple.com/documentation/devicediscoveryui/devicepairingview)
- [DevicePicker](https://developer.apple.com/documentation/devicediscoveryui/devicepicker)
- [Device picker initializer](https://developer.apple.com/documentation/devicediscoveryui/devicepicker/init%28_%3Aaccess%3Aonselect%3Alabel%3Afallback%3Aparameters%3A%29)
- [DDDevicePickerViewController](https://developer.apple.com/documentation/devicediscoveryui/dddevicepickerviewcontroller)
- [Default device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/default?changes=_6)
- [Permanent device-pairing access](https://developer.apple.com/documentation/devicediscoveryui/dddevicepairingaccess/permanent?changes=_7)
- [Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware?changes=_7)
- [Adopting Wi-Fi Aware](https://developer.apple.com/documentation/WiFiAware/Adopting-Wi-Fi-Aware)
- [Connecting devices for peer-to-peer Wi-Fi](https://developer.apple.com/documentation/wifiaware/connecting-paired-devices)
- [Building peer-to-peer apps](https://developer.apple.com/documentation/wifiaware/building-peer-to-peer-apps?changes=_4_5&language=objc)
- [WACapabilities](https://developer.apple.com/documentation/wifiaware/wacapabilities)
- [WAPairedDevice.allDevices](https://developer.apple.com/documentation/wifiaware/wapaireddevice/alldevices)
- [NetworkBrowser](https://developer.apple.com/documentation/Network/NetworkBrowser)
- [NetworkListener](https://developer.apple.com/documentation/network/networklistener)
- [NetworkConnection](https://developer.apple.com/documentation/network/networkconnection?changes=__2)
- [NetworkConnection Wi-Fi Aware information](https://developer.apple.com/documentation/network/networkconnection/wifiaware?changes=_1_7)
- [Wi-Fi Aware entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.wifi-aware?changes=__1)
- [WiFiAwareServices](https://developer.apple.com/documentation/bundleresources/information-property-list/wifiawareservices?changes=__1_9)
- [Network](https://developer.apple.com/documentation/network)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Swift concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
