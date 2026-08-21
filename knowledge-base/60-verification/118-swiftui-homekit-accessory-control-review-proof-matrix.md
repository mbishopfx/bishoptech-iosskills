# SwiftUI HomeKit and Matter accessory-control review proof matrix

This matrix separates SwiftUI rendering evidence from HomeKit authorization, shared-topology, physical-accessory, Matter commissioning, side-effect, accessibility, privacy, and release evidence. A preview, framework import, simulated characteristic, or dismissed setup sheet is not sufficient by itself.

## Evidence IDs

| ID | Evidence | Proves | Does not prove |
| --- | --- | --- | --- |
| H0 | Named target, SDK, capability, usage description, signing, entitlements, and extension artifacts | The selected target is configured for the route | Runtime authorization, a reachable accessory, or distribution approval |
| H1 | HomeKit allow/deny/revoke/restricted test | Authorization state and recovery UI | Complete home data, physical reachability, or production review |
| H2 | Deterministic topology fixture | Projection, identity, filtering, and stale/removal behavior | Current user’s home or real accessory state |
| H3 | HomeKit Accessory Simulator route | Simulated services, characteristics, read/write, notification, and error behavior | Physical radio/network behavior, real accessory safety, or release readiness |
| H4 | Signed physical-device plus representative accessory run | Target hardware, reachability, side-effect and reconciliation behavior | Every accessory class, every network, long-term reliability, or App Review |
| H5 | Matter commissioning run with named ecosystem/device | Request, criteria, onboarding, extension, credential, network, and post-setup behavior | Other Matter devices, unsupported targets, or production distribution |
| H6 | AI proposal fixtures and stale-revision rejection | Typed parsing, deterministic resolution, validation, and confirmation | Model quality for every phrase, physical safety, or command completion |
| H7 | Accessibility, performance, privacy, archive, and release packet | Separate quality and delivery gates | Any gate not explicitly recorded |

## Fixture contract

Every deterministic fixture should identify:

- home UUID and display name;
- room UUID and display name;
- accessory UUID, name, reachability, and room;
- service UUID, type, display name, and user-interactive status;
- characteristic UUID, type, properties, metadata, typed value, and notification support;
- source revision, last-seen time, pending command, and expected error;
- supported target/platform and whether the state is simulator, physical, sandbox, or production.

Do not use one Boolean fixture for every device. Include numeric units/ranges, enumerations, strings, sensor data, one-shot actions, stale values, unreachable accessories, removed objects, and notification failures.

## Configuration and authorization

| Gate | Test | Expected evidence | Common false claim |
| --- | --- | --- | --- |
| HomeKit capability | Inspect target capability and entitlements in the built artifact | Target contains the intended HomeKit entitlement | Source imports HomeKit, therefore the archive is configured |
| Usage description | Inspect Info.plist and trigger first-use prompt | NSHomeKitUsageDescription is present and truthful | A prompt screenshot proves the description is acceptable in review |
| Initial request | Fresh install or reset authorization | Allow and deny routes | One allowed run proves all permission states |
| Revocation | Revoke access in Settings while app has a cached projection | App removes unsafe controls and explains recovery | Cached cards remain valid after revocation |
| Restricted/unsupported | Test target/device restrictions | Clear unavailable state | A simulator has the same support as a signed physical target |
| Matter capability | Inspect request/extension configuration and target matrix | Supported/unsupported paths are explicit | MatterSupport import proves commissioning support |

## Shared topology and projection

| Scenario | Expected behavior | Evidence |
| --- | --- | --- |
| No homes | Show honest empty state and a user-requested create/setup path | Home manager fixture plus UI task |
| Multiple homes | Selected home is stable by UUID and visible in context | Switch-home task with service identity |
| Room rename or move | Projection updates without stale duplicate rows | External HomeKit change and refreshed snapshot |
| Accessory removal | Selection and drafts invalidate safely | Remove while detail/proposal is open |
| Accessory becomes unreachable | Preserve identity and last-known value with freshness cue | Simulator/physical network interruption |
| Service filtering | Only supported user-interactive services appear in primary task | Fixture with hidden, custom, and unrelated services |
| Unknown characteristic type | Diagnostic visibility without guessed control | Unknown-type fixture |
| External Apple Home change | SwiftUI updates and preserves focus where possible | Two-app or simulator-assisted change |

## Characteristic read/write

| Case | Required proof | Failure condition |
| --- | --- | --- |
| Readable value | Explicit read result maps to typed value and unit | Raw Any value displayed as trusted current state |
| Writable value | Properties and metadata permit the command | Blind write to a non-writable characteristic |
| Numeric range | Minimum, maximum, step, and unit validation | Slider can emit out-of-range values |
| Enumeration | Supported raw values map to known labels | App invents unsupported modes |
| Notification | Enable/disable lifecycle and callback mapping | Callback is treated as a complete history |
| Pending | Conflicting actions are serialized or intentionally handled | UI silently flips to desired value |
| Completion failure | Prior known state and retry path remain visible | Failed write remains optimistically committed |
| Physical transition | Completion plus later report are distinguishable | Request completion described as physical completion |
| Safety-sensitive action | Exact target and consequence are confirmed | Lock, door, alarm, or heater action runs from a suggestion |

## HomeKit setup

| Setup case | Evidence | Boundary |
| --- | --- | --- |
| System flow launch | User action starts documented setup API | A custom scanner is not equivalent to system setup |
| Code scan/manual entry | System flow handles supplied code and failure | Successful scan does not prove configured accessory |
| Naming/room | Returned home/accessory identifiers reload projection | Hard-coded card claims setup |
| Cancellation | Cancellation leaves no false accessory | Sheet dismissal treated as success |
| Denial/invalid code | Error maps to recovery without leaking payload | Error text exposes credentials or raw setup data |
| Accessory setup manager | Result home/accessory IDs are reconciled | Result object alone proves reachability |

## Matter commissioning

| Case | Required proof | Boundary |
| --- | --- | --- |
| Support check | Runtime support and target matrix | Compile alone proves support |
| Device criteria | Criteria fixture includes matching/non-matching devices | Broad all-devices filter is treated as authentication |
| Onboarding payload | Source, validation, and redacted logging policy | QR string stored in analytics |
| Extension handler | Credential, attestation, commissioning, and configuration paths | Extension class exists but is never invoked |
| Wi-Fi/Thread selection | System/extension result and error mapping | App assumes the device joined the intended network |
| Commissioned result | Ecosystem reload and identity/reachability check | Picker dismissal equals ready-to-control |
| Catalyst/unsupported | Explicit error or unavailable state | iOS proof generalized to Mac Catalyst |

## AI proposal and apply gate

| Fixture | Expected evidence | Rejection |
| --- | --- | --- |
| Exact service request | Typed proposal names current IDs and values | Fuzzy name silently selects a device |
| Ambiguous room/device | Review asks the person to choose | Model guesses |
| Stale topology revision | Proposal invalidates or re-evaluates | Old proposal writes after topology changed |
| Out-of-range value | Deterministic validator rejects | Model output becomes a clamped hidden side effect |
| Unwritable characteristic | Proposal explains unavailable control | AI claims success |
| Lock/door/heater/alarm | Explicit confirmation with exact consequence | Natural-language output runs command |
| Unreachable device | Proposal remains informational or offers retry | “Done” appears without a physical report |
| Sensitive context | Prompt scope is selected and minimized | Full home graph or credentials sent |

## SwiftUI and Liquid Glass

| Surface | Inspect | Required result |
| --- | --- | --- |
| Home context | Selected home/room visible and accessible | No ambiguous location |
| Service row | Identity, value, unit, freshness, reachability | No decorative state-only card |
| Pending write | Progress and cancellation/serialization | No false success |
| Failure | Explanation and recovery | No stuck glass animation |
| Setup preparation | Physical device, home destination, system handoff | No cloned pairing UI |
| Proposal review | Exact writes, source revision, warnings, apply decision | No direct model execution |
| Fallback | Reduced transparency, increased contrast, unsupported target | Same semantics without glass |

## Accessibility and alternate input

| Test | Evidence |
| --- | --- |
| VoiceOver | Labels identify home, room, service, state, freshness, and action; focus survives async updates |
| Voice Control | Commands match visible device/service labels |
| Switch Control | Primary control and setup recovery are reachable |
| Full Keyboard Access | Focus order, activation, and confirmation work without touch |
| Pointer/iPad | Hover/focus does not hide state or create accidental side effects |
| Dynamic Type | Large text preserves the primary control and result state |
| Reduced motion/transparency | No essential state depends on animation or blur |
| Localization | Long home/room/service names and units remain legible |

## Performance and privacy

| Gate | Measurement or review | Boundary |
| --- | --- | --- |
| Projection cost | Signpost topology refresh and snapshot build | Debug timing is not a universal performance claim |
| Observation scope | Count observed characteristics and callbacks | Whole-home polling assumed harmless |
| Write rate | Record debounce/serialization and command latency | Slider cadence generalized to every accessory |
| Energy | Physical-device sampling/network activity | Simulator power behavior generalized |
| Logging | Confirm no setup payloads, credentials, or private graph dumps | “Local AI” does not permit excessive collection |
| Lock/background | Review protected/private surface behavior | Foreground screen behavior generalized to lock screen |

## Archive and release

Before release, collect:

- built artifact entitlement and Info.plist inspection;
- selected SDK/deployment and target matrix;
- privacy and App Review purpose review;
- HomeKit/Matter extension embedding and principal-class evidence;
- signed archive and export/distribution result;
- physical-device run from the release build;
- TestFlight or production account/accessory evidence where applicable;
- accessibility and performance records;
- known unsupported accessory/platform list.

## Acceptance rule

The route is ready only when the named product path passes the evidence gates it claims. A preview, HomeKit Accessory Simulator fixture, Matter request object, local AI response, or successful compile can support development; none alone proves current home data, physical reachability, safe side effects, privacy, accessibility, or release readiness.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [Enabling HomeKit in your app](https://developer.apple.com/documentation/homekit/enabling-homekit-in-your-app)
- [Configuring HomeKit access](https://developer.apple.com/documentation/xcode/configuring-homekit-access)
- [NSHomeKitUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nshomekitusagedescription)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMService](https://developer.apple.com/documentation/homekit/hmservice)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [Characteristic types](https://developer.apple.com/documentation/homekit/characteristic-types)
- [HMAccessorySetupManager](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager)
- [HMAccessorySetupResult](https://developer.apple.com/documentation/homekit/hmaccessorysetupresult)
- [Configuring a home automation device](https://developer.apple.com/documentation/homekit/configuring-a-home-automation-device)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [Testing your app with the HomeKit Accessory Simulator](https://developer.apple.com/documentation/homekit/testing-your-app-with-the-homekit-accessory-simulator)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [Adding Matter support to your ecosystem](https://developer.apple.com/documentation/mattersupport/adding-matter-support-to-your-ecosystem)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceRequest.DeviceCriteria](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest/devicecriteria)
- [commissionDevice(in:onboardingPayload:commissioningID:)](https://developer.apple.com/documentation/mattersupport/matteradddeviceextensionrequesthandler/commissiondevice%28in%3Aonboardingpayload%3Acommissioningid%3A%29)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [HomeKit Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/homekit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
