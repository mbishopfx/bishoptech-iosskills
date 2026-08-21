# Core Bluetooth device proof matrix

Core Bluetooth claims cross permission, radio state, central/peripheral roles, GATT discovery, protocol trust, background scheduling, state restoration, physical effects, and optional iOS 26 Live Activity behavior. Record each boundary independently.

## Test record

| Field | Record |
| --- | --- |
| Target | Bundle ID, central/peripheral targets, extensions, target membership |
| SDK/deployment | Xcode, SDK, deployment target, availability checks |
| Privacy | NSBluetoothAlwaysUsageDescription and user-facing rationale |
| Background | UIBackgroundModes values, Live Activity use, task start/stop |
| Role | Central, peripheral, or dual-role |
| Device fixture | Product, firmware, service/characteristic register, protocol version |
| Physical setup | iPhone/iPad models, second device/accessory, distance, radio state |
| User state | Permission, Bluetooth on/off, selected device, trust/forget state |
| Restoration | Manager identifiers, termination method, restored keys, reconciliation |
| Transport | Connection, discovery, read/write/notify, queue/backpressure, errors |
| Domain result | Device acknowledgement, measured outcome, freshness, duplicate handling |
| AI state | Model/device availability, typed proposal, validation, external-upload audit |
| Accessibility | VoiceOver, Dynamic Type, Voice Control, Switch Control, reduced effects |
| Artifact | Signed archive, entitlements, privacy strings, build and release metadata |

Use a controlled accessory or synthetic test fixture. Do not record real device identifiers, room names, command payloads, or sensor data in shared evidence.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Does not prove it |
| --- | --- | --- |
| Bluetooth route configured | Target, usage description, role/background register, compile | Framework import |
| Permission rationale is present | Signed artifact and first-use UI | A source file string |
| Central can scan | Physical device, Bluetooth on, authorized manager, expected service fixture | Simulator discovery |
| Peripheral can advertise | Physical peripheral role, powered-on manager, advertising result | Local service object |
| Person selected the device | Selection interaction and app-owned device ID | First advertisement |
| Connection works | Physical connection/disconnection record | Discovered candidate |
| GATT graph matches | Service/characteristic discovery and UUID register | Device name |
| Read/write works | Payload, response/error, byte count, protocol version | Write callback without domain result |
| Notifications work | Subscription, ordered frames, backpressure, unsubscribe | One value callback |
| Physical command succeeds | Device-level acknowledgement or measurement | Transport acknowledgement |
| Background route works | Physical lock/background run with configured mode | Background capability checkbox |
| State restoration works | Termination/relaunch, stable identifier, restoration callback, reconciliation | App relaunch with a new manager |
| iOS 26 Live Activity route works | User-started ActivityKit surface plus background Bluetooth evidence on named target/device | A Live Activity preview |
| AI stays bounded | Typed proposal, validation log, redacted input, no arbitrary write | “AI” label |
| Accessibility works | Task matrix with assistive settings on physical device | Accessibility audit alone |
| Release ready | Final signed artifact, target/configuration, physical/system evidence | Debug compile or simulator run |

## Central scenarios

- [ ] Bluetooth permission is not determined; feature copy precedes the system prompt.
- [ ] Permission denied or restricted; manual/fallback mode remains usable.
- [ ] Bluetooth powered off; UI explains the radio state.
- [ ] Manager reports unsupported, resetting, or unknown.
- [ ] Scan is limited to the required service UUIDs.
- [ ] No candidates appear; retry and setup help are available.
- [ ] Two devices have identical advertised names.
- [ ] A candidate has the wrong service or protocol version.
- [ ] Person selects one candidate, then cancels connection.
- [ ] Connection succeeds and the expected services are discovered.
- [ ] Required characteristic is missing.
- [ ] Read succeeds with valid and malformed payloads.
- [ ] Write-with-response returns transport success and device rejection.
- [ ] Write-without-response reaches queue pressure and resumes through readiness.
- [ ] Notification frames arrive split, duplicated, out of order, or too large.
- [ ] Device changes services or firmware while connected.
- [ ] Connection drops during a confirmed command.
- [ ] App forgets/removes the selected device.

## Peripheral and dual-role scenarios

- [ ] Peripheral manager is powered off, unauthorized, or unsupported.
- [ ] Service add fails and the app does not advertise as ready.
- [ ] Advertising starts/stops and the UI reflects the actual state.
- [ ] Central subscribes and unsubscribes.
- [ ] Central read/write request is validated and answered with the correct ATT result.
- [ ] Notification queue fills; bounded backpressure prevents data loss or unbounded memory.
- [ ] A second physical device discovers and connects.
- [ ] Central and peripheral roles run without cross-role state corruption.
- [ ] Role teardown stops advertising, notifications, and pending work.

## Background, restoration, and Live Activity scenarios

| Scenario | Evidence |
| --- | --- |
| Foreground-only | Scan/connect/read/write from an unlocked physical device |
| bluetooth-central | Background discovery/connection within documented system limits |
| bluetooth-peripheral | Background service availability and central interaction within limits |
| Termination | Manager is recreated with the same restoration identifier |
| Central restoration | Restored peripheral/scan keys are reconciled and stale objects rejected |
| Peripheral restoration | Restored service/advertising/subscription state is reconciled |
| iOS 26 Live Activity | User starts bounded task, Activity is visible, app backgrounds, Bluetooth work is observed, task ends/cancels |
| Battery/radio interruption | Radio off, phone call/Siri/lock/interruption, recovery and user explanation |
| Duplicate event | Duplicate callbacks do not duplicate a command or durable domain result |

Record OS build, device model, app state, Bluetooth state, task start time, and whether the app was terminated. A successful foreground connection is not background proof.

## Privacy and security checks

- [ ] Usage description explains the specific feature, not generic “Bluetooth access.”
- [ ] Raw advertisements, device identifiers, RSSI, and characteristic data are redacted from logs.
- [ ] Device selection and protocol verification are visible before side effects.
- [ ] Commands carry a request ID and duplicate/replay policy.
- [ ] A cryptographic or pairing result, where required, is checked separately from transport connection.
- [ ] Forget/delete removes app-owned device identity and retained telemetry per policy.
- [ ] AI inputs contain only approved fields and no raw radio dump.
- [ ] External model upload is blocked or explicitly governed.
- [ ] Sensitive device state is not exposed in widgets, notifications, or Live Activities by default.
- [ ] Physical effect claims use device-reported outcomes or remain unknown.

## Accessibility matrix

- [ ] VoiceOver can understand scan purpose, selected device, connection state, freshness, and result.
- [ ] VoiceOver focus returns to the selected-device summary after async discovery.
- [ ] Dynamic Type keeps Confirm, Cancel, Retry, Forget, and error recovery reachable.
- [ ] Voice Control names are distinct for duplicate devices and commands.
- [ ] Switch Control reaches scanning, selection, confirmation, and removal.
- [ ] Reduce Motion does not remove state meaning.
- [ ] Reduce Transparency and increased contrast preserve state differences.
- [ ] RTL, localization, long names, missing data, and error strings fit.
- [ ] Keyboard/pointer focus and non-gesture alternatives work where supported.

## Evidence vocabulary

| Term | Meaning |
| --- | --- |
| discovered | System reported a candidate matching the scan |
| selected | Person chose the candidate |
| connected | Core Bluetooth reported a connection |
| compatible | Expected GATT/protocol schema passed validation |
| trusted | App-specific identity/authorization rule passed |
| subscribed | Notification path is enabled |
| framed | Payload passed app protocol decoding |
| acknowledged | Transport or device returned an acknowledgement; specify which |
| completed | Domain result was observed and recorded |
| restored | System relaunched/reprovided manager state and app reconciled it |
| stale | Cached value is not current enough for the product claim |
| unknown | App cannot prove the physical/domain outcome |

## Sources

- [Core Bluetooth](https://developer.apple.com/documentation/corebluetooth)
- [CBCentralManager](https://developer.apple.com/documentation/corebluetooth/cbcentralmanager)
- [CBCentralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate)
- [CBPeripheral](https://developer.apple.com/documentation/corebluetooth/cbperipheral)
- [CBPeripheralDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheraldelegate)
- [CBPeripheralManager](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanager)
- [CBPeripheralManagerDelegate](https://developer.apple.com/documentation/corebluetooth/cbperipheralmanagerdelegate)
- [CBManagerAuthorization](https://developer.apple.com/documentation/corebluetooth/cbmanagerauthorization)
- [Transferring data between Bluetooth Low Energy devices](https://developer.apple.com/documentation/corebluetooth/transferring-data-between-bluetooth-low-energy-devices)
- [Central manager state restoration options](https://developer.apple.com/documentation/corebluetooth/central-manager-state-restoration-options)
- [Peripheral manager state restoration options](https://developer.apple.com/documentation/corebluetooth/peripheral-manager-state-restoration-options)
- [Core Bluetooth background processing for iOS apps](https://developer.apple.com/library/archive/documentation/NetworkingInternetWeb/Conceptual/CoreBluetooth_concepts/CoreBluetoothBackgroundProcessingForIOSApps/PerformingTasksWhileYourAppIsInTheBackground.html)
- [NSBluetoothAlwaysUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsbluetoothalwaysusagedescription)
- [UIBackgroundModes](https://developer.apple.com/documentation/bundleresources/information-property-list/uibackgroundmodes)
- [ActivityKit](https://developer.apple.com/documentation/activitykit)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
