# SwiftUI Core Bluetooth and nearby-accessory review proof matrix

This matrix separates SwiftUI rendering from Bluetooth authorization, radio state, discovery, identity, GATT, protocol, background, energy, physical-device, accessibility, and release evidence.

## Evidence IDs

| ID | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| B0 | Named target, SDK, Info.plist, usage description, role, background modes, signing | The intended target is configured | Radio availability or a trusted accessory |
| B1 | Authorization and CBManager state matrix | Permission/poweredOn/off/resetting/unsupported behavior | Identity, GATT compatibility, or physical command result |
| B2 | Deterministic discovery fixtures | Filtering, duplicate policy, candidate expiration, and UI | A discovered device is the intended physical product |
| B3 | GATT fixture | Service/characteristic/descriptor discovery and property mapping | Protocol trust or physical safety |
| B4 | Protocol adapter fixtures | Encoding/decoding, bounds, framing, checksum, version, and errors | Radio reliability, accessory firmware, or product outcome |
| B5 | Physical central route | Real accessory connection, response, notification, and reconnection | Every hardware model or release distribution |
| B6 | Physical peripheral/two-device route | Advertising, subscription, read/write, and device-to-device convergence | Background behavior or broad platform support |
| B7 | Background/restoration route | Declared mode, wake, restore callback, checkpoint, bounded processing | Always-on execution or immunity from termination |
| B8 | AI proposal fixtures | Typed proposal, stale-session rejection, and confirmation | Model quality for every phrase or physical effect |
| B9 | Accessibility, energy, privacy, archive, release | Separate quality and delivery gates | Any unrecorded gate |

## Fixture contract

Each fixture should record:

- target and selected SDK/deployment;
- central, peripheral, or both roles;
- authorization and CBManager state;
- candidate peripheral ID, name, advertisement services, manufacturer/service data policy, and discovery timestamp;
- expected service, characteristic, descriptor, property, and maximum write length;
- protocol version, payload bytes or redacted fixture identifier, checksum/authentication result, and typed value;
- connection/session revision, reported value, desired value, pending command, notification state, and error;
- simulator, physical, background, or release-build context.

Never make a name-only discovery fixture the identity proof.

## Target and permission

| Gate | Test | Expected result | False claim |
| --- | --- | --- | --- |
| Usage description | Inspect built Info.plist | NSBluetoothAlwaysUsageDescription is present and specific | A prompt screenshot proves the target is correctly configured |
| Authorization | notDetermined, allowedAlways, denied, restricted | UI explains recovery and avoids unsafe controls | allowedAlways means poweredOn |
| Manager state | unknown, resetting, poweredOn, poweredOff, unauthorized, unsupported | State-specific UI and command gating | A manager object means Bluetooth is ready |
| Role configuration | central/peripheral/both | Target artifacts match the route | A framework import supports every role |
| Background mode | Inspect UIBackgroundModes if claimed | Declared role is explicit and user-justified | A background string gives unlimited execution |

## Discovery and identity

| Case | Required evidence | Rejection |
| --- | --- | --- |
| Service filter | Scan returns intended service candidates | Broad scan treated as product identity |
| Duplicate advertisements | Duplicate policy and stop condition | One callback equals one device |
| Candidate expiry | Stale candidate becomes unavailable or refreshable | Old scan row remains trusted |
| Same display name | Multiple devices remain distinguishable | Name selects device silently |
| Random/system identifier | Product identity binds after protocol validation | UUID treated as serial/authentication |
| RSSI | Approximate candidate clue only | RSSI proves nearest or intended device |
| Manufacturer data | Validated or hidden from UI | Raw bytes become trusted metadata |
| User cancellation | stopScan and session cancellation | Radio remains active after leaving route |

## Connection and GATT discovery

| Case | Evidence | Boundary |
| --- | --- | --- |
| Connection request | Connecting state and cancellation | connect call proves ready |
| didConnect | Delegate installed and discovery begins | Link proves product protocol |
| Service discovery | Required service UUIDs found | All services are safe to expose |
| Characteristic discovery | Required endpoints and properties mapped | UUID alone proves payload semantics |
| Descriptor discovery | Formatting/user-description metadata when required | Descriptor text is authentication |
| Missing endpoint | Read-only/unsupported state and recovery | App invents an endpoint |
| Disconnect | Stale snapshot and reconnect policy | In-memory peripheral means connected |
| Reconnect | Identity and protocol handshake repeat | Reconnect proves prior identity without validation |

## Protocol and command semantics

| Fixture | Required result | False claim |
| --- | --- | --- |
| Valid versioned packet | Typed domain value and revision | Raw Data shown as product state |
| Short/long packet | Decode rejection or bounded error | Parser reads beyond contract |
| Bad checksum/authentication | Packet rejected and session marked unsafe | UI shows decoded value |
| Unknown protocol version | Unsupported state and upgrade/support path | App guesses field layout |
| Read | Value, timestamp, and source update | Read means physical safety |
| Write with response | Transport response and later reported state separate | Callback means physical effect complete |
| Write without response | Sent/best-effort state, no delivery claim | UI says delivered |
| Maximum length | Encoder respects selected write type limit | Payload truncates silently |
| Notification | Subscription, sequence, deduplication, and decode | Notification is acknowledgment/history |
| Fragmentation | Reassembly timeout and bounds | Partial packet becomes value |
| Concurrent commands | Serialization or documented concurrency | Race changes device state unexpectedly |

## Central role

Collect:

- scan filter and stop evidence;
- connection/disconnection callbacks;
- services/characteristics/descriptors;
- read and write response;
- notification enable/failure and report;
- reconnect and stale-value behavior;
- protocol handshake and identity record.

The physical central route should run on a representative accessory with the release configuration where possible.

## Peripheral role and two-device route

If the app advertises:

- record peripheral manager poweredOn state;
- record published services/characteristics and permissions;
- verify advertisement and service discovery from the central device;
- test read/write/subscription requests;
- test notification delivery and unsubscribe;
- test background behavior if claimed;
- test both devices signed with the intended build configuration.

A local peripheral preview or one-device unit test does not prove two-device communication.

## Background and restoration

| Test | Required evidence | Boundary |
| --- | --- | --- |
| Foreground-only route | Suspension behavior and restart recovery | Foreground callback generalized to background |
| bluetooth-central | Background discovery/connection behavior on physical device | UIBackgroundModes means continuous scanning |
| bluetooth-peripheral | Background advertising/request behavior | Foreground advertising generalized |
| State preservation | Manager restoration options and restored state | Declaration without termination/relaunch |
| willRestoreState | Reinstantiation, restored peripherals/subscriptions, checkpoint | Restored object accepted without handshake |
| Process termination | Durable checkpoint and safe reconstruction | App cannot be terminated |
| Bounded wake | Work completes quickly and returns | AI/full sync runs on every wake |

## SwiftUI and Liquid Glass

| Surface | Inspect | Required result |
| --- | --- | --- |
| Discovery | Candidate identity, stale state, cancel | No trusted device claim |
| Connection | Connecting/discovering/verifying/ready | No premature control |
| Value card | Reported/desired/freshness/unit | No optimistic canonical state |
| Command result | Sent/acknowledged/reported/failed | Transport and physical result separate |
| Glass group | Bounded related controls and readable status | No blur-only truth |
| Fallback | Opaque/material/reduced effects | Same semantic task without Liquid Glass |
| AI review | Exact accessory/session/characteristic/value/warnings | No direct model execution |

## AI proposal rejection matrix

| Proposal | Expected rejection or gate |
| --- | --- |
| Device selected by fuzzy name only | Ask for deterministic selection or reject |
| Stale session revision | Refresh and review again |
| Unknown UUID | Reject before encoding |
| Invalid payload/value | Reject with typed validation message |
| No write response support | Label sent/best-effort; require report for completion |
| Security-sensitive command | Explicit confirmation and verified session |
| Missing protocol handshake | Keep read-only or setup state |
| Prompt contains pairing key | Remove secret and record privacy failure |

## Accessibility and alternate input

| Test | Required evidence |
| --- | --- |
| VoiceOver | Device, service, connection, verification, freshness, and command semantics |
| Voice Control | Visible device/command names activate the same gate |
| Switch Control | Scan cancel, connect, primary action, and recovery are reachable |
| Keyboard/pointer | Selection, focus, commands, and confirmation work on iPad |
| Dynamic Type | Long names and result states remain readable |
| Reduced motion | No essential state depends on animation |
| Increased contrast/transparency | Glass fallback preserves hierarchy |
| Localization | Units, device names, errors, and response semantics fit |

## Energy and privacy

| Gate | Evidence |
| --- | --- |
| Scan duration | Start/stop timestamps and service filter |
| Duplicate policy | Allow-duplicates decision and measurement need |
| Discovery scope | Required services/characteristics only |
| Subscription scope | Notification list and cleanup |
| Reconnect policy | Retry limits, backoff, and user visibility |
| Background work | Wake reason, bounded duration, checkpoint |
| Logging | Redaction of identifiers, advertisements, credentials, payload secrets |
| Device data | Retention, export, cloud/model boundary, and user choice |

## Archive and release

Inspect the release artifact for:

- NSBluetoothAlwaysUsageDescription;
- role and background configuration;
- embedded frameworks/extensions if any;
- signing and entitlements;
- target/deployment/SDK;
- privacy and App Review declarations;
- physical-device run from the archive;
- known accessory/protocol/OS limitations.

## Acceptance rule

The route is ready only when the claims match the evidence. A Core Bluetooth import, discovery row, connected callback, simulated packet, local AI response, preview, or compile does not prove identity, trust, delivery, battery behavior, accessibility, privacy, physical effect, or release readiness.

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [About Core Bluetooth](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/AboutCoreBluetooth/Introduction.html)
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
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [Core Bluetooth Background Processing for iOS Apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [Best Practices for Interacting with a Remote Peripheral Device](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/BestPracticesForInteractingWithARemotePeripheralDevice/BestPracticesForInteractingWithARemotePeripheralDevice.html)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
