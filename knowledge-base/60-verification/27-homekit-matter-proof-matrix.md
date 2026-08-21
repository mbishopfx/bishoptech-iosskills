# HomeKit and Matter proof matrix

This matrix prevents a HomeKit or Matter feature from being called complete because a home card rendered or a simulator accessory responded once. The route crosses entitlements, user authorization, a shared database, physical devices, system-owned setup, network/accessory state, safety-sensitive side effects, and sometimes an extension or ecosystem service.

## Evidence levels

| Level | Evidence | What it can prove |
| --- | --- | --- |
| L0 | Source and route review | The selected HomeKit/Matter symbols, setup model, HIG vocabulary, and known limitations are documented. |
| L1 | Deterministic model/fixture test | Projection, typed characteristic validation, stale-state reducer, proposal decoding, and failure policy behave predictably. |
| L2 | HomeKit Accessory Simulator or controlled setup fixture | The target can exercise selected service reads/writes, callbacks, and UI states without requiring every physical accessory. |
| L3 | Signed physical-device run | Entitlement, authorization, real accessory reachability, characteristic behavior, notifications, setup, and hardware/environment behavior are exercised on supported hardware. |
| L4 | Matter commissioning/system run | The MatterSupport system flow, onboarding payload, permission, network choice, attestation/commissioning, ecosystem result, and extension process are exercised. |
| L5 | Release evidence | Archive entitlements, privacy review, App Store configuration, supported-platform matrix, and any ecosystem/provider distribution state agree. |

## Target and capability

| Claim | Minimum evidence | Do not infer |
| --- | --- | --- |
| The target can use HomeKit | L0 + target capability/entitlement inspection + L3 signed target run | A framework import, simulator, or source snippet does not prove the signed entitlement or App Review configuration. |
| The target can use MatterSupport | L0 + selected SDK availability + target/extension membership + L4 | HomeKit access to an existing Matter accessory does not prove the app can commission a new Matter device. |
| The usage description is present and useful | Built Info.plist inspection + allow/deny run | A source Info.plist entry does not prove the archived target contains it or that the copy explains the user benefit. |
| Platform support is accurate | Compile each selected destination and runtime support/unsupported fixtures | iOS support does not imply Mac Catalyst, iPadOS, watchOS, or every device supports the same Matter route. |

## Authorization and topology

| Route state | Required fixture/evidence | Acceptance boundary |
| --- | --- | --- |
| First access request | Signed physical target, explain-before-request screen, system prompt | The app requests only when a useful HomeKit task is ready. |
| Authorized | Manager callback, homes loaded, selected-home UI | A granted permission does not mean a home exists or an accessory is reachable. |
| Denied/restricted | Permission denial, relaunch, Settings change | The app has a useful fallback and does not fabricate device state. |
| No home | Empty home list, create/setup choice | No blank device cards are presented as real home state. |
| Multiple homes | At least two homes with overlapping room/service names | The selected home is visible and references never silently cross homes. |
| External topology change | Add/remove/rename in Apple Home or another HomeKit app | The app reconciles instead of relying on a stale copied graph. |
| Blocked/unreachable accessory | Controlled accessory failure or simulator equivalent plus physical run when relevant | The app labels last-known data as stale and prevents unsafe writes where necessary. |

## Characteristic state and control

| Claim | Required evidence | Acceptance boundary |
| --- | --- | --- |
| Read current state | Explicit read with success, error, timeout/unreachable, and stale-cache fixtures | value is treated as last-seen state until freshness is known. |
| Render a control | Property/metadata fixture for readable, writable, event-capable, hidden, range, and unit states | The UI does not offer a write the characteristic cannot perform. |
| Write a value | Valid, invalid, out-of-range, rejected, and accessory-transition runs | The local control does not become canonical merely because an API call started. |
| Observe changes | Notification/delegate change from Apple Home, another app, and the accessory | No claim is made that the callback is a complete historical event stream. |
| Handle removal | Accessory/service/characteristic disappears during a read/write/proposal | Focus and pending work recover without applying to a new object at the same list index. |
| Safety-sensitive control | Lock/garage/heater/alarm scenario with confirmation, cancellation, and failure | Copy describes the exact side effect and outcome; no AI or animation bypasses the confirmation policy. |

## HomeKit setup

| Claim | Required evidence | Acceptance boundary |
| --- | --- | --- |
| Add an accessory | System setup flow, valid device, cancelled flow, invalid/unsupported device, post-setup refresh | Dismissing setup is not by itself proof of reachability or complete product configuration. |
| Directed setup | HMAccessorySetupRequest fields, target home/room, suggested name, payload/response path | The request’s target and resulting accessory are reconciled from current HomeKit state. |
| Custom accessory configuration | Relevant service filtering, custom characteristic route, changed values in Apple Home | Custom UI adds useful behavior without cloning the entire Apple Home configuration model. |
| Accessory Simulator support | Deterministic simulator fixture for each service used | Simulator behavior is a development aid, not proof of physical radio, firmware, range, or safety behavior. |

## Matter commissioning

| Claim | Required evidence | Acceptance boundary |
| --- | --- | --- |
| Matter route is available | Runtime isSupported branch on supported and unsupported platform/device | The app keeps a useful fallback when the route is unavailable. |
| Onboarding payload accepted | Valid payload, invalid payload, expired/duplicate/unsupported device fixtures | Raw QR/setup payload is treated as untrusted until the supported API accepts it. |
| System pairing consent | User-started MatterAddDeviceRequest.perform with allow and cancel | The app does not imply that pairing occurs without explicit system/user control. |
| Network selection | Wi-Fi/Thread scan or default-network run, missing network, cancellation | The app does not collect or log sensitive network credentials unnecessarily. |
| Attestation/commissioning | Extension request handler credential validation, attestation failure, commission success/failure | A selected device is not called ready until ecosystem state and reachability are reconciled. |
| Multiple ecosystems | Accessory already paired elsewhere and supported ecosystem transfer/access route | A Matter device’s multi-ecosystem state and user choice are not collapsed into one app flag. |
| Matter extension process | Signed extension target, plist principal class, terminated/relaunched extension path | A host-app preview does not prove the extension’s real process lifecycle. |

## Scenes, triggers, and AI

| Claim | Required evidence | Acceptance boundary |
| --- | --- | --- |
| Create a scene | Typed characteristic writes, invalid target/value rejection, named scene, current HomeKit state | A sentence or local draft is not an action set. |
| Execute a scene | Explicit user action, action-set result, unspecified action-order handling, partial/error presentation | Do not promise a strict device order unless separately verified. |
| Schedule or trigger | Time/event trigger creation, persistence, recurrence, sensor change, cancellation, and delivery | A local schedule row or timer is not proof of HomeKit automation execution. |
| AI drafts a scene | Fixed prompt/context fixtures, typed decode, deterministic service resolution, stale invalidation, confirmation | Generated text and canonical home state remain separate. |
| AI refusal/fallback | Unknown room/device, ambiguous request, unavailable model, denied HomeKit access, safety-sensitive request | The model cannot silently execute a side effect or claim current state it cannot observe. |

## Design, accessibility, and privacy

| Claim | Required evidence | Acceptance boundary |
| --- | --- | --- |
| Native Apple-like surface | HIG review, semantic controls, Liquid Glass state variants, compact/wide layouts | Native polish is not pixel replication of Apple Home or a custom Apple icon. |
| VoiceOver task completion | Physical or signed device with VoiceOver for select home, inspect state, control, confirm, retry | Labels alone do not prove the full task is operable. |
| Dynamic Type/localization | Largest supported text sizes, long room/device names, unit/localization fixtures | A screenshot at default text size is insufficient. |
| Reduced transparency/motion | Settings enabled with pending/stale/error/success states | Decorative material effects cannot carry essential state. |
| Privacy boundary | Prompt/context audit, no raw home graph or unnecessary credentials in logs/AI | A local model or permission grant does not make sensitive data safe by default. |

## Evidence packet

Record a packet per route with:

~~~text
feature:
target and bundle:
commit/build:
sdk and deployment target:
device model and os:
homekit capability and usage description:
matter capability or extension target:
home/accessory/simulator fixture:
authorization state:
topology:
characteristics and scenarios:
setup/pairing result:
scene/trigger result:
ai proposal fixture and confirmation:
accessibility settings:
privacy/retention review:
logs and screenshots:
known failures:
release claim supported:
~~~

Keep screenshots, logs, and device recordings tied to the build and scenario. A successful physical write may prove one accessory and one state; it does not prove all supported service types, firmware versions, homes, regions, network conditions, or release configurations.

## Claim language

Use precise statements:

- “The signed target displayed a HomeKit characteristic from a physical accessory after authorization.”
- “The controlled fixture rejected a non-writable characteristic and retained stale state on unreachable.”
- “Matter commissioning was exercised on the named device with a valid onboarding payload and the selected ecosystem configuration.”
- “The AI generated a typed scene proposal that required confirmation; no model output directly performed a HomeKit write.”

Avoid:

- “HomeKit works” after one simulator preview.
- “Matter pairing is complete” after a dismissed sheet.
- “The AI controls the house” when it only drafted a proposal.
- “The glass dashboard is native” without accessibility, state, and device evidence.

## Sources

- [HomeKit](https://developer.apple.com/documentation/homekit)
- [HMHomeManager](https://developer.apple.com/documentation/homekit/hmhomemanager)
- [HMHome](https://developer.apple.com/documentation/homekit/hmhome)
- [HMAccessory](https://developer.apple.com/documentation/homekit/hmaccessory)
- [HMCharacteristic](https://developer.apple.com/documentation/homekit/hmcharacteristic)
- [HMActionSet](https://developer.apple.com/documentation/homekit/hmactionset)
- [Interacting with a home automation network](https://developer.apple.com/documentation/homekit/interacting-with-a-home-automation-network)
- [Performing accessory setup](https://developer.apple.com/documentation/homekit/hmaccessorysetupmanager/performaccessorysetup%28using%3Acompletionhandler%3A%29)
- [MatterSupport](https://developer.apple.com/documentation/mattersupport)
- [MatterAddDeviceRequest](https://developer.apple.com/documentation/mattersupport/matteradddevicerequest)
- [MatterAddDeviceExtensionRequestHandler](https://developer.apple.com/documentation/mattersupport/matteradddeviceextensionrequesthandler)
- [Matter support in iOS](https://developer.apple.com/apple-home/matter/)
- [HomeKit HIG](https://developer.apple.com/design/human-interface-guidelines/homekit/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
